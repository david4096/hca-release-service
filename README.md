This software attempts to make it easy to create studies of the functional genomic data from the Human Cell Atlas by providing scalable, easy-to-use services.

One can think of the HCA as a large table spread across many locations with each row a sample and each column a feature. The purpose of this software is to gather and assemble data and then offer it using a few simple, well-defined, interfaces.

At any given time, a list of sample_ids and feature_ids is what is needed to generate a Study. In this way, it is possible for the community to decide on what data is involved in a study and easily communicate central points of analysis.

## Services

Essentially, celldb-hca will take a list of sample identifiers and features and create an addressable location that can be used to download some, or all of the resulting data. These API methods are described in the AWS Gateway SDK so they can be easily integrated into existing infrastructure.

### Report generation

A simple API for generating reports from a Study.

A Jupyter Notebook is maintained that will perform analyses agreed upon by the community. This Notebook is ran "headless" and the resulting figures are written to a file that can be viewed without Python or programming experience.

#### hca python module

df = hca.df('Study-ID')

From the report notebook one can see clearly the line used to access the data. A dataframe is generated from a study identifer.

### File package

The Study is stored as timestamped files in a cloud storage system, including HDF5 sparse matrix files.

### HTTP API

Access sparse functional genomic data simple HTTP requests.

### Query service

A simple webapp for downloading data from a Study.

## Initiating a study

Initating a Study is an asynchronous process. First, the requester creates the list of samples and features that will be used for the Study. 

This list is sent to an HTTP service that will immediately return an Error, or a bucket location where the Study will be placed.


## Routes

```
/create_study
	Accepts POST list of feature_ids and sample_ids and returns a bucket location.
/study/abc
	Accepts GET to return the bucket location, and POST to access slices of the 
```

To properly demonstrate we have created a TSV of two datasets and stored them in S3. These are expected to be indexed and accessible via Elastic Search.

On request, a set of samples and features than spans both datasets is merged and the results are written to a new S3 location.

This S3 location contains a Jupyter Notebook with some metrics and rudimentary analysis, and can be used to continue analysis.

To demonstrate the facility of this approach, we offer a python module that will allow dataframes to be downloaded by Study ID.

To finish today: split up a TSV and upload to two locations

`hca-demo n-datasets k-samples l-features`

A simple boto3 batch script that will upload random gene-cell matrices to as many buckets requested with a total number of samples and features matching those requested.

Lambda to Batch

Lambda gives a map of bucket IDs to sample IDs (and passes down the list of features) and creates a new bucket with that data manifest in it (`manifest.json`). The resulting message could be indexed by ES.

A batch job gathers the data from each of the buckets and filters for the requested sample IDs, writing each resulting file to the new bucket with a filename that matches it batch process.

`hca-filter from-bucket-id to-bucket-id`

Will create a new file in `to-bucket-id` that matches the `sample_ids` defined for `from-bucket-id` in the `to-bucket-id`'s manifest. The filename is the `from-bucket-id`.

When all of the batch jobs for requesting data have finished, the files are merged into a single Study TSV and HDF5 file.

`hca-merge bucket-id`

This will create the single TSV file for all of the data in the bucket and write to that bucket.

Once these files have been merged, the report files are created.

`hca-report bucket-id`

This runs a Jupyter Notebook in headless mode for the given bucket and writes the results and figures to the bucket.

* A website with a record of all of the requested studies is also available.
