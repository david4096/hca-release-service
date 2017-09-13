from chalice import Chalice
import boto3

from cStringIO import StringIO
import hashlib
import json

app = Chalice(app_name='davidcs-hca-release-service')
app.debug = True

# This bucket stores application state including mocking files.
APPLICATION_BUCKET_NAME = 'davidcs-hca-release-service'


def my_buckets(prefix='davidcs'):
    """
    List all the buckets with the given prefix.
    :param: prefix
    :return:
    """
    return filter(
        lambda x: x['Name'].find(prefix) != -1,
        boto3.client('s3').list_buckets()['Buckets'])


@app.route('/')
def index():
    try:
        buckets = my_buckets()
    except Exception as e:
        print(e)
        buckets = []
    return {'buckets': [x['Name'] for x in buckets]}


@app.route('/initialize', methods=['POST'])
def initialize():
    """
    This function initializes a release by accepting a list of sample
    identifiers. These sample_ids will be used to construct a manifest and
    this file will be added to a new bucket.

    By hashing the list of sorted sample_ids we can create a predictable
    identifier scheme.

    :return: The bucket that was created
    """
    request = app.current_request
    body = request.json_body
    sorted_sample_ids = sorted(body['sample_ids'])
    # This allows us to create a predictable scheme where the same release
    # won't be generated twice.
    release_id = hashlib.sha256("\n".join(sorted_sample_ids)).hexdigest()[0:20]
    release_bucket_name = "davidcs-hca-release-{}".format(release_id)
    s3 = boto3.client('s3')
    # First create a bucket for the release
    try:
        print(s3.create_bucket(Bucket=release_bucket_name,
                               CreateBucketConfiguration={
                                   'LocationConstraint': 'us-west-2'}))
    except Exception as e:
        print(e)
    # Now that we've created a bucket, we'll add a manifest that tells where
    # to find the samples.
    # FIXME this will be replaced with a set of ES queries.
    # Download index from application bucket, this is for demonstration only
    index_filename = 'index.json'
    s3.download_file(
        Key=index_filename,
        Bucket=APPLICATION_BUCKET_NAME,
        Filename='/tmp/' + index_filename)
    index = {}
    with open('/tmp/' + index_filename, 'r') as f:
        index = json.load(f)
    # Then write a manifest to the release bucket
    # This manifest is a map of buckets to the sample IDs that are in each of
    # them that map the requested sample_ids.
    manifest = {}
    print(index)
    for bucket, sample_ids in index.items():
        manifest[bucket] = filter(lambda x: x in sorted_sample_ids, sample_ids)
    # write it to a file to upload
    manifest_filename = "manifest.json"
    with open('/tmp/' + manifest_filename, 'w') as f:
        f.write(json.dumps(manifest))
    # then upload the file with the same name as the bucket
    s3.put_object(
        Bucket=release_bucket_name,
        Key=manifest_filename,
        Body=StringIO(json.dumps(manifest)).read())
    # s3.upload_file(
    #     Filename='/tmp/' + manifest_filename,
    #     Bucket=release_bucket_name,
    #     Key=manifest_filename)
    return {'release_bucket': release_bucket_name}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
