# Notebook

Welcome to the Neurodata Without Borders format official tutorial! NWB is a format for publishing and exchanging neuroscience data. The purpose of this tutorial is to demonstrate the process of preparing data for publication in NWB. We will cover:

- the layout of an NWB file
- the primary NWB abstractions: `Module`, `Interface`, and `TimeSeries`
- NWB schemas and extensions

We will explore these concepts by analyzing some rodent hippocampal data and appending the result to an existing NWB file. 

## Software Dependencies

This tutorial requires the following software:

- **INSERT API DEPENDENCY HERE**
- [HDFView](https://www.hdfgroup.org/products/java/hdfview/), a graphical interface for browsing HDF5 files
- [Python](https://www.python.org/), version 2 or 3
- Python libraries:
    - [h5py](http://docs.h5py.org/en/latest/)
    - [scikit-learn](http://scikit-learn.org/stable/index.html)

## What is NWB for?

In the course of neurophysiological data analysis, an analyst is faced with many kinds of data. It is useful to imagine these data in a directed graph structure. At the beginning of the pipeline, we have raw data, as recorded in the experiment. As one moves down the pipeline, we obtain processed forms of the data; further on, branches in the pipeline may merge.

![](flow_chart.png)

Some kinds of processing are so common that their results are likely to be used by most consumers of a dataset. For example, the experiment that provided the data for this tutorial produced 64-channel 20 Khz extracellular recordings. This data is large, computationally unwieldy, and somewhat opaque. Many users will be more interested in working with a downsampled form (LFP) or extracted spike trains. NWB was designed with this sort of scenario in mind; it defines conventions for the packaging of processed forms of the data together with the raw source and metadata. In this way, simple data analysis workflows can be encapsulated in a single HDF5 file. This makes NWB a good **data exchange format**-- adherence to NWB conventions will help potential collaborators get up to speed with your data.

However, at its present stage of development NWB is not, however a strong **working format**. The current version lacks key features (e.g. robust inter-file links, provenance annotation for datasets) that are necessary to efficiently capture a structured, evolving, many-branched data analysis workflow. In the future, we intend to incorporate these features and develop NWB into a full-fledged working format.

## Tutorial Overview

In this tutorial, we will work with extracellular recordings from the hippocampus of navigating rats. The recordings were taken from a rat running back and forth on a linear track to obtain a water reward. Embedded in the hippocampal formation are two different multielectrode arrays, each having 4 shanks, with each shank having 8 recording sites ("channels"). We use a single session here, spanning {T:} seconds. The data was published by the [Buzsaki Lab](http://www.buzsakilab.com/). This data and data from many similar sessions is hosted on [CRCNS](https://crcns.org/data-sets/hc/hc-3).

Working through the tutorial will give you experience reading, writing, and browsing an NWB file by performing some analysis on a pre-processed form of the experimental recordings. Specifically, we are going to project the LFP into a new space (identified with independent component analysis) and segment the temporal dimension of the data into distinct trials (passes of the linear track). We will plot the projected LFP against animal position to reveal LFP features that selectively activate in specific locations across trials (behavior analogous to that of hippocampal place cells). Finally, we will write our results to the NWB file we started with. Because the data we will generate does not fit into pre-defined NWB structures, we will need to define an **extension** using the *specification language*.

The specific steps we will take are:

- locate the LFP and position information in the NWB file
- load the LFP and position data (with `h5py`)
- downsample the LFP
- bandpass-filter the LFP to the theta range
- perform independent component analysis on the downsampled, filtered LFP
- segment the position timeseries into distinct traversals of the track ("trials")
- plot the energy of basis functions learned through ICA against trial and position
- create a new `Module` to hold our analysis results
- write the projected representation of the LFP to an `Interface` within the new `Module`
- write the segmented trial information to an `Interface` within the `Module`
- describe the new `Interfaces` with a schema written in the [NWB Specification Language]{T:link}

### (1) locate the LFP and position data in the NWB file

First, let's orient ourselves to the structure of NWB. Open `ec014.468.nwb` with HDFView. You should see this:

![](hdfview1.png)

Notice that there are 5 top-level datasets and 6 top-level groups. While most metadata is stored in the `/general` group, there are a few items that were judged important enough to include at the top level. These include:

- `file_create_date`: timestamp for the creation of this NWB file
- `identifier`: globally unique identifier for this NWB file
- `nwb_version`: version number for this NWB file
- `session_description`: a summary of the experiment that yielded the data stored in this file
- `session_start_time`: the absolute time at which the session began

The 6 groups contain the following kinds of data:

- `/acquisition`: Directly recorded data streams
- `/analysis`: free-form, unspecified data analysis products; intended for internal use, not publication. Published analysis products should be placed in a processing `Module` in `/processing`, with an accompanying `schema`.
- `/epochs`: Time slices of the experiment (e.g. subexperiments, trials)
- `/general`: Experimental metadata (e.g. protocol, notes, description of hardware)
- `/processing`: Data analysis products. `/processing` has a special structure that we cover in more detail below.
- `/stimulus`: Data pushed into the system (e.g. video stimulus, sound, voltage, etc) and/or secondary representations of that data (e.g. measurements of something used as a stimulus)

More details about these groups can be found in the [official documentation]({T:link}). In this tutorial, we are interested only in the contents of `/processing`. `/acquisition`, `/epochs`, and `/stimulus`, are empty for our session (the raw data would normally be present in `/acquisition`, but we do not provide it in order to keep the file size small).

#### /processing

{T: explain /processing scheme of this file}

The contents of `/processing` have the most complex structure in NWB. This is because `/processing` is intended to contain machine-readable representations of arbitrary analysis products. The contents are always described by a three-level hierarchy. A particular NWB abstraction corresponds to each level of the hierarchy.

- `Modules` are stored at the top-level of `/processing`. A `Module` is just an HDF5 group that declares its contents in an attribute `interfaces`. Because a `Module's` internal structure is fully described by the listed interfaces, `Modules` are not declared in a specification and may be named arbitrarily.
- `Interfaces` are the top-level contents of `Modules`. `Interfaces` are groups that contain one or more `TimeSeries` and possibly related metadata. The contents of the `Interface` must be declared in the file's schema. Thus the name of the `Interface` group must match:
    - an entry in the containing `Module's` `interfaces` attribute 
    - an `Interface` declaration in the file's schema
- `TimeSeries` are found inside `Interfaces` (and other places in an NWB file). A `TimeSeries` is a group that contains a time series and associated metadata. All `TimeSeries` are instances of an associated `TimeSeries` class, which is part of a hierarchy analogous to that of object-oriented programming languages. The core `TimeSeries` hierarchy is defined in the core NWB schema. It provides a set of `TimeSeries` intended to cover a broad range of data types. All `TimeSeries` must provide two key datasets:
    - `data`: contains the time-aligned data. Time must be on the first axis.
    - `timestamps` or `starting_time`: `timestamps` is a 1-dimensional dataset containing a timestamp for each row of `data`. These timestamps are relative to the experiment start time. Alternatively, `starting_time` is a single timestamp (also relative to experiment start time) that stores the start of the `TimeSeries`. `starting_time` must have an attribute `rate` which gives the sample rate. This allows the full list of timestamps to be derived from `starting_time`.

![HDFView snapshot of processing/LFP]()
{T:insert image}

Click on `/processing` to examine its contents. You should see 2 groups inside: `lfp` and `position`. These are `Modules`. Click on `lfp`. Notice that its `interfaces` attribute (visible in the bottom pane of HDFView) has a single entry "LFP", and it contains a single group `LFP` matching this entry. `LFP` is a built-in interface type. That is, it is defined in NWB's core schema. It must contain one or more instances of the `TimeSeries` class `ElectricalSeries`. Click on `LFP`; you should see it contains 9 groups: `all`, `shank_1`, `shank_2`, ..., `shank_12`. `all` contains the LFP recorded from all 64 electrodes. The `shank_<N>` groups contain HDF5 region references into the `all` dataset (corresponding to the channels on each shank). They are provided for convenience. In this tutorial we will work with `all`.

Now let's find the position. The position representation we will use is a product of processing overhead video of the experiment. The subject had two LEDs mounted on its head; the X and Y coordinates of each LED were extracted. Expand `/processing/position` in HDFView. Like `lfp`, `position` is a `Module` that declares a single `Interface` `Position`. The `Position` interface is defined in the NWB core schema. It must contain one or more `TimeSeries` of class `SpatialSeries`. Like `LFP`, our `Position` interface includes an `all` timeseries, containing the coordinates of both LEDs, and `led_1` and `led_2`, which are region references to the coordinates of each separate LED. As with `LFP`, in this tutorial we will work with `all`.

### (2) load the LFP and position data

We will now load the LFP into memory. At present, NWB does not have a read API. Therefore we will use Python's mature HDF5 interface library `h5py`. First we need to create an `h5py` `File` object. Because we will be adding to the source file, you should open it in `'r+'` mode:

```python
import h5py
data = h5py.File('ec014.468.nwb', 'r')
```

For the remainder of this tutorial, we will read our NWB file through the `File` object `data`. Now let's load the LFP time series. `h5py` provides it as a `Dataset` object that behaves similarly to a `numpy` array.

```python
lfp = data['/processing/lfp/LFP/all/data']
```

The matrix now stored in `lfp` is the primary `data` field of a `TimeSeries`. The shape is `(4947125,99)`. The first dimension is time, and the second is channel number. Time is always the first dimension for NWB TimeSeries. Notice that there is also a `starting_time` dataset inside `all`. It's `rate` attribute tells us that the sample rate is 1250 Hz. Thus the temporal extent of our LFP data is 4947125/1250 = 3,9656 seconds, or approximately 66 minutes.

Now let's load `position`:

```python
pos = data['/processing/position/Position/all/data']
```

The shape of `pos` is `(152246,4)`. Like `lfp`, the first dimension of `pos` represents time. The second dimension contains two pairs of X and Y coordinates that capture the position of two LEDs mounted on the head of the subject. Though `pos` and `lfp` are aligned to the same timebase, notice that the temporal dimension of `pos` is much smaller than that of of `lfp`. This is because `pos` is sampled at a much lower rate than `lfp`; 39.0625 Hz, according to `Position/all/starting_time.rate`.

### (3) downsample and bandpass-filter the LFP

Since we are interested in comparing the LFP with the position. we will only look at the LFP at the time points when the animal is known to occupy a specific location. Before proceeding further, we will downsample `lfp` so that it has the same temporal extent as `pos`. We perform the downsampling with a call to a function residing in the `buzsaki_hc.py` module included with this tutorial. Because the focus of this tutorial is the structure of NWB, rather than the implemnetation of signal processing techniques, all of our analysis will be executed via calls to this module. 

```python
import buzsaki_hc as bhc
pos_rate = data['/processing/position/Position/all/starting_time'].attrs['rate']
lfp_rate = data['/processing/lfp/LFP/all/starting_time'].attrs['rate']
ds_lfp = bhc.downsample(lfp, lfp_rate, pos_rate)
```

When a rodent is moving, the hippocampus shows prominent theta-band (5-11 Hz) activity. We are going to look specifically at this activity. To extract this activity, we will bandpass filter the downsampled LFP.

```python
filt_lfp = bhc.bandpass_filter(ds_lfp, 5.0, 11.0, order=1)
```

## (3) Perform independent component analysis on the LFP

Independent Component Analysis is a technique for separating a multivariate signal into a set of additive components. Beginning with a set of observed signals, we model our signal at each time point as a linear combination of fixed basis functions. The contributions of the individual basis functions are assumed to be statistically independent. You can learn more about ICA [here](http://www.stat.ucla.edu/~yuille/courses/Stat161-261-Spring14/HyvO00-icatut.pdf). The model can be summarized as:

$$X = AS$$

Where $X$ is the "observed signal", $A$ is the "mixing matrix" (whose columns are the aforementioned basis functions), and $S$ is the "source signal" (with each row correpsonding to the coefficients for one basis function).

Here, our observed signal is the all-channel filtered LFP that we have loaded into `filt_lfp`. The basis functions extracted from applying ICA to LFP signals have no straightforward physiological interpretation. However, when the LFPs are taken from the hippocampus of navigating rats, the basis functions behave like place cells; that is, their activities (given by the learned coefficients) are locked to particular locations in the environment.

We call the `bhc` module to perform ICA for us. This yields two matrices: `sources`, inc

```python
sources, components = bhc.lfp_ica(filt_lfp)
```

## (4) 

Now that we have the mixing matrix and coefficients, we need to write them to the NWB file. But where? How do our mixing matrix and coefficient series map into NWB? A core concept in NWB is the `TimeSeries` hierarchy {T: link}. The NWB core does not define a `TimeSeries` type suitable for representing our ICA results. Therefore, we have defined a new `TimeSeries` type, `DictionarySeries`, in our extension. In a `DictionarySeries`, a set of basis functions is stored as columns of `dict` and the primary `data` field contains the coefficients for each basis function at each time point:

{T: required properties for dictionary series}

We now write the result of our ICA analysis to a new `DictionarySeries` with `h5py`. As per the NWB specification, our `DictionarySeries` is represented as an HDF5 group. We mark it as a `DictionarySeries` by filling in the `ancestry` attribute. Note that the specification requires that we provide all ancestors in this field, so we also list `TimeSeries`. We provide a variety of other required elements of the `DictionarySeries`, as defined by our extension file and the inherited requirements from the root `TimeSeries` type. Because this is a tutorial, we show the explicit creation of each element; however, normally one would call an API that would hide the details of these operations.

```python
s = data['/processing/LFP/LFP timeseries']
g = data.create_group('/analysis/lfp_ica')
g['data'] = ica_coeff
g['dict'] = ica_mix
g.attrs['ancestry'] = [ 'TimeSeries', 'DictionarySeries' ]
g.attrs['description'] = "ICA decomposition of LFP at /processing/lfp"
g.attrs['neurodata_type'] = 'TimeSeries'
g.attrs['source'] = '???'  # TODO
g['data'].attrs['conversion'] = '???'  # TODO
g['data'].attrs['resolution'] = '???'  # TODO
g['data'].attrs['unit'] = '???'  # TODO
g['num_samples'] = '???'  # TODO
g['starting_time'] = s['starting_time']
g['starting_time'].attrs['rate'] = s['starting_time'].attrs['rate']
```

## (3) Converting Position to a Unidimensional Quantity

{T: PCA link}

In order to see the position-tuning of our extracted independent components, we need to represent position as a unidimensional quantity. Currently, our position time series is 4-dimensional. However, because the subject was on a linear track, the X and Y coordinates of each LED are tightly correlated. Because the distance between LEDs is fixed, the coordinates of different LEDs are likewise correlated. Thus all the dimensions in our position-matrix are pairwise-correlated, and we can efficiently represent position with a single vector. We obtain this vector by applying principal component analysis (PCA) to our position matrix. Like ICA, PCA is a popular decomposition method for multivariate signals. PCA finds a change of basis for a signal such that variance is concentrated in the fewest number of axes. Due to the high pairwise correlations in our signal, PCA will allow us to find a single axis that captures most of the variance. We will use the coordinate of each time point along this axis as our 1-dimensional position signal.

Let's apply PCA to our position data. `scikit-learn` provides a PCA implementation `PCA`:

```python
from sklearn.decomposition import PCA
model = PCA(n_components=1)
pos_pca = model.fit_transform(pos)[0]
```

By plotting the extracted signal, we can see that it resembles motion back-and-forth along a linear track. We use `matplotlib`'s PyPlot interface to handle plotting:

```python
import matplotlib.pyplot as plt
plt.plot(pos_pca)
```

## (4) Segmenting Position into Trial Epochs

We now have position as a single, unidimensional time series. In order to see the relationship between LFP feature activation and position, we need to segment this time series into separate passes of the track ("trials"), and further partition these trials by the direction the animal was moving. The latter step is important because place cells are direction-dependent in a linear environment, and our extracted LFP features are too.

We achieve this by dividing the track into three regions: a center and two ends. We are interested only in the center region, as the rat sometimes lingers at the ends. We code each point in time according to the region the rat was located in, and then search for continuous stretches in the center region. As a result, we get two Mx2 arrays, one for left-to-right trials and one for right-to-left trials. Each row contains the temporal bounds of one trial.

```python
import re

def get_track_segment(i):
		x = posx[i]
		if x < bounds[0]:
			return 'l'
		if x > bounds[1]:
			return 'r'
		return 'c'

segments = [ get_track_segment(x, bounds) for x in posx ]

left_to_right_pat = re.compile('(?<=l)c+(?=r)')
left_to_right_trials = [ (m.start, m.start + len(m)) for m in left_to_right_pat.finditer(segments) ]

right_to_left_pat = re.compile('(?<=r)c+(?=l)')
right_to_left_trials = [ (m.start, m.start + len(m)) for m in right_to_left_pat.finditer(segments) ]
```

NWB core provides a `SpatialSeries` class which matches our use case. We write our extracted unidimensional position to a new instance of `SpatialSeries` in the `/analysis` group:

{T: required properties for spatial series}

```python
g = data.create_group('/analysis/pos_pca')
g['data'] = pos_1d
```

{T: remaining code to complete pos timeseries}


We perform this by {T:XXX}, implemented in `buzsaki_hc.extract_trials()`. This function returns two two-dimensional matrices (`left` and `right` below). Each row contains the starting and ending time index for a track pass in the left or right direction, respectively.

```python
left, right = bhc.extract_trials(pos_1d)
```

Because time series in NWB are aligned to a common time base and segmentation of a session's time course is a common problem, NWB dedicates a top-level directory (`epochs`) to storing slice information.

```python
g = 
```

## (5) Plotting Component Activation vs Position

We now have our ICA-derived representation of LFP and trial-separated position. We can visualize the relationship of feature activation to position using heat maps of the feature coefficients. In the grid of plots below, each row corresponds to one basis function. The left column corresponds to leftward trials, and the right column to rightward trials. Within each plot, the x-axis represents position and the y-axis represents trial number. The pixel value represents the average coefficient value at the corresponding position and trial. Thus, light-colored columns (as visible in BFs 2 and 3) represent consisent selectivity of a basis function for a particular location. This is the same behavior we see with place cells.

```python

```

## (6) Writing analysis products to a new `Module`

The final step is to write our analysis products to the NWB file. We will put our data in a new `Module`. We'll call it `ffp_analysis`. As described above, `Module`s document their contents by listing the `Interfaces` they contain. We will populate `ffp_analysis` with two `Interfaces`; one for decomposed LFP and one for trial segments. However, the NWB core schema does not define appropriate interfaces for these two data types. We'll need to define our own in a separate schema. Here is the 

Every NWB file defines one or more schemas in `/general/specifications`.  

```python
data.create_group('/processing/ffp_analysis')
```

```python
data.create_group('/processing/position')
data.
```

The NWB core schema does not 

## Source Data Structure

- the raw data acquired during the experiment
- simply processed forms of the raw data (e.g. down-sampled or filtered time series)
- downstream analysis products that depend on multiple data sources (e.g. statistical models relating stimulus to recordings)
- experimental metadata

Each of these data types maps to one or more of NWB's 6 top-level directories:

Below we discuss the contents of each of the groups used for the behavioral rodent data that are the subject of this tutorial. `/epochs` and `/stimulus` are not used, so they are not listed. It is useful to follow along by visually inspecting the file with a graphical interface for HDF5 files (e.g. [HDFView](https://www.hdfgroup.org/products/java/hdfview/)).

### /acquisition

There are two acquired input streams for this experiment: the video of the navigating rodent, and the extracellular recordings taken from the rodent's hippocampus.

{T: where are these data}

### /analysis

Our starting NWB file contains an empty `/analysis` group. This is where we will be writing the results of our analysis, including:

- an ICA model of the local field potentials
- a segmentation of the time course of the experiment into trials (passes of teh linear track)

### /general

Metadata describing the behavioral task, experimental subject, lab, etc.

### /processing

Contains three subgroups. The structure of each subgroup is involved and will be discussed in more detail later. The high-level contents of the subgroups are:

- `lfp`: a downsampled version of the raw data
- `head_position`: a numerical representation of the animal's position extracted from the video
- `spikes`: spike trains extracted from the recordings, and the intermediate data generated in the course of this extraction

- `pos_1d`: a unidimensional representation of position obtained by extracting the first [principal component]() of the four-dimensional LED position matrix
- `ica_mix`: the mixing matrix learned by performing independent component analysis on the 
- `ica_coeff`: the coefficients ("sources") corresponding to the independent components
- {T: trial separation}

