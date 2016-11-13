The functionality covered in this tutorial is available in the Github package at {T:link}

v1 TODO
- documentation
- validation

v2 TODO
- let people know that the code can be called

## (7) Validating the File

The NWB API offers a validator. Here we'll run the validator to ensure that the file we've just written conforms to NWB specifications. The validator can be run as a standalone script with `python -m nwb.nwb_validate myfile.nwb`. Since we are limited to a Python context in this notebook, we will access it via it's Python interface:

```python
```

When the validator returns {T: fill in valid results}


## Conclusion

Some kinds of processing are so common that their results are likely to be used by most consumers of a dataset. For example, the experiment that provided the data for this tutorial produced 64-channel 20 Khz extracellular recordings. This data is large, computationally unwieldy, and somewhat opaque. Many users will be more interested in working with a downsampled form (LFP) or extracted spike trains. NWB was designed with this sort of scenario in mind; it defines conventions for the packaging of processed forms of the data together with the raw source and metadata. In this way, simple data analysis workflows can be encapsulated in a single HDF5 file. This makes NWB a good **data exchange format**-- adherence to NWB conventions will help potential collaborators get up to speed with your data.

However, at its present stage of development NWB is not, however a strong **working format**. The current version lacks key features (e.g. robust inter-file links, provenance annotation for datasets) that are necessary to efficiently capture a structured, evolving, many-branched data analysis workflow. In the future, we intend to incorporate these features and develop NWB into a full-fledged working format.

## How Strict is NWB?

In any bookstore, you can find many different books. All books share the same basic form factor (NWB's top-level hierarchical structure). In an American book store, most of them will be composed of English words (NWB's TimeSeries and Interface primitives). However, there are many ways to arrange words in English to express the same idea. In NWB, there are many ways to arrange the provided primitives to represent a processing pipeline.
