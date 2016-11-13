{T: using Buzaski package / module}
{T: TimeSeries hierarchy}
{T: extension}
{T: slices}

- description of NWB
- description of Buzsaki dataset

for grant:
While future NWB versions are intended to capture evolving data analysis workflows, the current version of is not suited to this task. There are two important features that the current version lacks:

- Unique-identifier-qualified links between files. The importance of this feature is best understood by analogy to the Web.
Much as the consists of HTML documents that link to each other in a global address space with URLs, 


# Notebook

Welcome to the Neurodata Without Borders format official tutorial! NWB is a format for publishing and exchanging neuroscience data. The purpose of this tutorial is to demonstrate the process of preparing data for publication in NWB. We will cover:

- the layout of an NWB file
- the primary NWB abstractions: `Module`, `Interface`, and `TimeSeries`
- NWB schemas and extensions

We will explore these concepts by analyzing some rodent hippocampal data and appending the result to an existing NWB file. 

## What NWB Is and Is Not

A note before we start: at its present stage of development, NWB is a **data exchange format**. That is, it is a good format for publishing data in a relatively polished form. Adherence to NWB conventions will help potential collaborators understand the structure of your data. NWB is *not*, however, a strong **working format**. While future NWB versions are intended to capture evolving data analysis workflows, the current version of is not suited to this task. There are two important features that the current version lacks:

- Unique-identifier-qualified links between files. The importance of this feature is best understood by analogy to the Web.
Much as the consists of HTML documents that link to each other in a global address space with URLs, 


that are necessary for the development of distributed graphs of individual NWB files.

designed to store the provenance metadata for each node in a data analysis workflow. 

## NWB Basics

NWB was designed to {T:}. In the course of neurophysiological data analysis, an analyst is faced with many kinds of data. It is useful to imagine these data in a directed graph structure. At the beginning of the pipeline, we have raw data, as recorded in the experiment. As one moves down the pipeline, we obtain processed forms of the data that have been altered for storage or computational reasons; further on, branches in the pipeline may merge.

{T: flowchart}

An analyst can quickly obtain a complex graph of data products. An ideal working format for this kind of data analysis would have several features:

- 


## Tutorial Overview

We will work with extracellular recordings from the hippocampus of navigating rats. The recordings were taken from a rat running back and forth on a linear track to obtain a water reward. Embedded in the hippocampal formation are two different multielectrode arrays, each having 4 shanks, with each shank having 8 recording sites ("channels"). We use a single session here, spanning {T:} seconds. The data was published by the [Buzsaki Lab](http://www.buzsakilab.com/). This data and data from many similar sessions is hosted on [CRCNS](https://crcns.org/data-sets/hc/hc-3).

The purpose of this tutorial is to give you experience reading, writing, and browsing an NWB file. We do this by performing some analysis on a pre-processed form of the experimental recordings. Specifically, we are going to project the LFP into a new space, identified with independent component analysis. We will plot the results against animal position to reveal place-cell-like activation patterns in some of the learned basis functions.

This will require us to:

- locate the LFP and position information in the NWB file
- load the LFP and position information (with `h5py`)
- perform independent component analysis on the LFP
- segment the position timeseries into distinct traversals of the track ("trials")
- plot the energy of basis functions learned through ICA against trial and position
- create a new `Module` to hold our analysis results
- write the projected representation of the LFP to an `Interface` within the new `Module`
- write the segmented trial information to an `Interface` within the `Module`
- describe the new `Interfaces` with a schema written in the [NWB Specification Language]{T:link}

{T:specification description}

### (1) locate the LFP and position information in the NWB file

First, let's orient ourselves to the structure of NWB. Open `ec014.468.nwb` with HDFView. You should see this:

{T: screenshot}

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

The contents of `/processing` have the most complex structure in NWB. This is because `/processing` is intended to contain machine-readable representations of arbitrary analysis products. The contents are **always** described by a three-level hierarchy. A particular NWB abstraction corresponds to each level of the hierarchy.

- `Modules` are stored at the top-level of `/processing`. A `Module` is just an HDF5 group that declares its contents in an attribute `interfaces`. Because a `Module's` internal structure is fully described by the listed interfaces, `Modules` are not declared in a specification and may be named arbitrarily.
- `Interfaces` are the top-level contents of `Modules`. `Interfaces` are groups that contain one or more `TimeSeries` and possibly related metadata. The contents of the `Interface` must be declared in the file's schema. Thus the name of the `Interface` group must match:
    - an entry in the containing `Module's` `interfaces` attribute 
    - an `Interface` declaration in the file's schema
- `TimeSeries` are found inside `Interfaces` (and other places in an NWB file). A `TimeSeries` is a group that contains a time series and associated metadata. All `TimeSeries` are instances of an associated `TimeSeries` class, which is part of a hierarchy analogous to that of object-oriented programming languages. The core `TimeSeries` hierarchy is defined in the core NWB schema. It provides a set of `TimeSeries` intended to cover a broad range of data types. All `TimeSeries` must provide two key datasets:
    - `data`: contains the time-aligned data. Time must be on the first axis.
    - `timestamps` or `starting_time`: `timestamps` is a 1-dimensional dataset containing a timestamp for each row of `data`. These timestamps are relative to the experiment start time. Alternatively, `starting_time` is a single timestamp (also relative to experiment start time) that stores the start of the `TimeSeries`. `starting_time` must have an attribute `rate` which gives the sample rate. This allows the full list of timestamps to be derived from `starting_time`.

Click on `/processing` to examine its contents. You should see 3 groups inside: `lfp`, `position`, and `spikes`. These are `Modules`. Click on `lfp`. Notice that its `interfaces` attribute has a single entry "LFP", and it contains a single group `LFP` matching this entry. The contents of `LFP` are defined in the NWB core schema. It must contain one or more instances of the `TimeSeries` class `ElectricalSeries`. Click on `LFP`; you should see it contains 9 groups: `all`, `shank_1`, `shank_2`, ..., `shank_8`. `all` contains the LFP recorded from all 64 electrodes. The `shank_<N>` groups contain HDF5 region references into the `all` dataset (corresponding to the channels on each shank). They are provided for convenience. In this tutorial we will work with `all`.

We will now load the LFP into memory using Python's mature HDF5 interface library `h5py`. First we need to create an `h5py` `File` object. Because we will be adding to the source file, you should open it in `'w+'` mode:

```python
import h5py
data = h5py.File('ec013.157.analysis.nwb', 'w+')
for k in [ 'acquisition', 'epochs', 'general', 'processing', 'stimulus' ]:
  data[k] = h5py.ExternalLink('ec013.157.nwb', "/{0}".format(k))
data.create_group('/analysis')
```

Let's go ahead and load the data:

```python
lfp = data['/processing/shank_0/LFP/LFP timeseries']
```

{T: processing contents image}

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

# Background

# Tutorial

{T: where to put this}
- `lfp`: a downsampled (1.25 KHz from the original 20 KHz) form of the extracellular voltage traces ("LFP")
- `pos_4d`: a two-dimensional representation of the location of each of two LEDs mounted on the subject's head, previously extracted through image processing
- `spk`: spike trains for each of neuron that could be identified from the raw voltage traces

A c

Our approach here will be to create a new NWB file that references the source data in the original. We will achieve this using HDF5's linking mechanism. Specifically, we will create a file `ec014.465.ica_analysis.nwb` that links all top level groups except for `/analysis` to the original.

In the course of analysis, we will generate the following additional time series:

- `pos_1d`: a unidimensional representation of position obtained by extracting the first [principal component]() of the four-dimensional LED position matrix
- `ica_mix`: the mixing matrix learned by performing independent component analysis on the 
- `ica_coeff`: the coefficients ("sources") corresponding to the independent components
- {T: trial separation}

## Step 1: Open NWB file with h5py

The first thing we need to do is get access to our NWB file. NWB does not yet have a Python-based read-write API. We therefore use the popular HDF5 Python library `h5py`, which lets us read and write arbitrary paths in an HDF5 file. See [here]() for a tutorial on `h5py`.

All access to our NWB file will be via the defined `h5py` `File` instance `data`.

## Step 2: Introduction to NWB TimeSeries

We are going to perform some analysis on the local field potential ("LFP"). The LFP is just a downsampled version (1.25 KHz) version of the raw voltages. Because there were 64 recording channels in this session, the LFP measurement at each point in time is a 64-dimensional vector. Taken together, all LFP measurements form a time series. In NWB, time series are represented as HDF5 groups. The LFP time series for this dataset is located at `/processing/shank_0/LFP/LFP timeseries`:

{T: interfaces}

The 

A group is identified as a `TimeSeries`, by it's `neurodata_type` attribute:

```python
print(lfp.attrs['neurodata_type'])
```




## Step 3: Decomposing the Local Field Potential

Independent Component Analysis is a technique for separating a multivariate signal into a set of additive components. Beginning with a set of observed signals, we model our signal at each time point as a linear combination of fixed basis functions. The contributions of the individual basis functions are assumed to be statistically independent. You can learn more about ICA [here](http://www.stat.ucla.edu/~yuille/courses/Stat161-261-Spring14/HyvO00-icatut.pdf). The model can be summarized as:

$$X = AS$$

Where $X$ is the "observed signal", $A$ is the "mixing matrix" (whose columns are the aforementioned basis functions), and $S$ is the "source signal" (with each row correpsonding to the coefficients for one basis function).

Here, our observed signal is the LFP. The basis functions extracted from applying ICA to LFP signals have no straightforward physiological interpretation. However, when the LFPs are taken from the hippocampus of navigating rats, the basis functions behave like place cells; that is, their activities (given by the learned coefficients) are locked to particular locations in the environment.

The primary data matrix is stored under `data`

All NWB timeseries use the first axis for time. This matrix is {T:dims}. 

Because ICA is a commonly used technique, there are various high-quality open-source implementations. Here we will use the `FastICA` implementation provided by `scikit-learn`.

```python
from sklearn.decomposition import FastICA
model = FastICA()
ica_coeff = model.fit_transform(samples)
ica_mix = model.mixing_
```

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

## Step 3: Converting Position to a Unidimensional Quantity

In order to see the position-tuning of our extracted independent components, we need to represent position as a unidimensional quantity. Currently, position is represented in 4 dimensions (the X and Y coordinates of two head-mounted LEDs). Because the subject was on a linear track, the X and Y coordinates of each LED are tightly correlated. Because the distance between LEDs is fixed, the coordinates of different LEDs are likewise correlated. Thus all the dimensions in our position-matrix are pairwise-correlated, and we can efficiently represent position with a single vector. We obtain this vector by applying principal component analysis (PCA) to our position matrix. Like ICA, PCA is a popular decomposition method for multivariate signals. `scikit-learn` provides a PCA implementation `PCA` that we use here. PCA finds a change of basis for a signal such that variance is concentrated in the fewest number of axes. Because all components of our observed position signal are mutually correlated, PCA here allows us to find a single axis that captures most of the variance. We use the coordinate of each time point along this axis as our 1-dimensional position signal. You can learn more about PCA [here]().

```python
from sklearn.decomposition import PCA
pos = data['/processing/position/data']
model = PCA(n_components=1)
pos_pca = model.fit_transform(samples)[0]
```

By plotting the extracted signal, we can see that it resembles motion back-and-forth along a linear track:

```python
plot
```

NWB core provides a `SpatialSeries` class which matches our use case. We write our extracted unidimensional position to a new instance of `SpatialSeries` in the `/analysis` group:

{T: required properties for spatial series}

```python
g = data.create_group('/analysis/pos_pca')
g['data'] = pos_1d
```

{T: remaining code to complete pos timeseries}

## Step 4: Segmenting Position into Trial Epochs

We now have position as a single, unidimensional time series. In order to see the relationship between LFP component activation and position, we need to segment this time series into separate passes of the track ("trials"), and further partition these trials by the direction the animal was moving. The latter step is important because place cells are direction-dependent in a linear environment.

We perform this by {T:XXX}, implemented in `buzsaki_hc.extract_trials()`. This function returns two two-dimensional matrices (`left` and `right` below). Each row contains the starting and ending time index for a track pass in the left or right direction, respectively.

```python
left, right = bhc.extract_trials(pos_1d)
```

Because time series in NWB are aligned to a common time base and segmentation of a session's time course is a common problem, NWB dedicates a top-level directory (`epochs`) to storing slice information.

```python
g = 
```

## Step 5: Plotting Component Activation vs Position

We now have our ICA-derived representation of LFP and trial-separated position. We can visualize the relationship of basis function activation to position using heat maps of the basis function coefficients. In the grid of plots below, each row corresponds to one basis function. The left column corresponds to leftward trials, and the right column to rightward trials. Within each plot, the x-axis represents position and the y-axis represents trial number. The pixel value represents the average coefficient value at the corresponding position and trial. Thus, light-colored columns (as visible in BFs 2 and 3) represent consisent selectivity of a basis function for a particular location. This is the same behavior we see with place cells.

We now have independent LFP components and trial-separated position, we can visualize the relationship of component activation to position. We will construct heat maps of component activation, with trial number on the Y-axis and position on the X-axis. 
