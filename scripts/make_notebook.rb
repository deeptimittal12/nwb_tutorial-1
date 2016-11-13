#!/usr/bin/env ruby
# ENV['BUNDLE_GEMFILE'] = '/Users/smackesey/stm/dotfiles/Gemfile'
# require 'bundler/setup'
# require 'stmenv'
require 'json'

fpath = ARGV.first

TEMPLATE = <<JSON
{
"metadata": {
"kernelspec": {
 "display_name": "Python 3",
 "language": "python",
 "name": "python3"
},
"language_info": {
 "codemirror_mode": {
  "name": "ipython",
  "version": 3
 },
 "file_extension": ".py",
 "mimetype": "text/x-python",
 "name": "python",
 "nbconvert_exporter": "python",
 "pygments_lexer": "ipython3",
 "version": "3.5.2"
}
},
"nbformat": 4,
"nbformat_minor": 0
}
JSON

def jsonify(seg)
  ctype, content =
    case seg
    when /^```python/ then ['code', seg.split("\n")[1..-2].join("\n")]
    when /^```json/ then ['markdown', seg.split("\n")[1..-2].map { |ln| '    ' + ln }.join("\n")]
    else ['markdown', seg]
    end
  rec = {
    :cell_type => ctype,
    :metadata => {},
    :source => [ content ]
  }
  rec.merge!(:outputs => [], :execution_count => nil) if ctype == 'code'
  rec
end

EXCLUDE = %w[
  hdfv_published_position
  hdfv_published_lfp
]

segs, curr = [], nil

content = File.read(fpath)

content.split("\n").each do |ln|
  case ln
  when /^#/ 
    segs << curr if curr
    segs << [ln]
    curr = []
  when /^```(python|json)/
    segs << curr
    curr = [ln]
  when /^```/
    curr << ln
    segs << curr
    curr = []
  when ->(x) { EXCLUDE.any? { |x| ln.match(x) } }
  else
    curr ||= []
    curr << ln
  end
end
segs << curr

# require "pry"; binding.pry

cells = segs.map { |seg| jsonify(seg.join("\n").strip) }

###################################
########### INSERT PLOTS
###################################

SOURCE_PATH = '/Users/smackesey/stm/code/explore/rctn_hippo_01/notebooks/July_1/phase_precession.ipynb'
nbdata = JSON.load(File.read(SOURCE_PATH))
plots = nbdata['cells'].find { |c| c['execution_count'] == 114 }['outputs']
target_cell = cells[ cells.index { |c| c[:source].first =~ /## \(4\)/ } + 2 ]
target_cell[:outputs] = plots

# require "pry"; binding.pry
final = JSON.load(TEMPLATE).merge('cells' => cells)
# require "pry"; binding.pry
puts JSON.pretty_generate(final)
