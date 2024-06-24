import argparse
import logging
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam
from google.cloud import storage
from xml.etree import ElementTree
from io import StringIO
import json
from google.cloud import bigquery
 
 
def parse_into_dict(xmlfile):
    import xmltodict
    json_data = xmltodict.parse(xmlfile,attr_prefix='')
    def change_keys(obj, convert):
        if isinstance(obj, (str, int, float)):
                return obj
        if isinstance(obj, dict):
                new = obj.__class__()
                for k, v in obj.items():
                        new[convert(k)] = change_keys(v, convert)
        elif isinstance(obj, (list, set, tuple)):
                new = obj.__class__(change_keys(v, convert) for v in obj)
        else:
                return obj
        return new
    def convert(k):
return k.replace('-','_')
    json_data2=change_keys(json_data,convert)
    json_data_final = json.dumps(json_data2['Data'])
 
    return json_data_final
 
def addlines(lines):
    return ' '.join(lines)
 
def addtobq(data):
    bigquery_client = bigquery.Client()
    json_data=json.loads(data)
    table_id = 'hsbc-11597902-fsmiasp-dev.dataset01.xm_load'
    storage_client = storage.Client()
    for blob in storage_client.list_blobs('fsmiaspdev-dataproc-user-amit',prefix='dataflow/results'):
        print(str(blob))
        uri='gs://fsmiaspdev-dataproc-user-amit/'+str(blob.name)
    print("+++++++=============",uri)
 
    job_config = bigquery.LoadJobConfig(
    source_format='NEWLINE_DELIMITED_JSON'
    )
    # uri='gs://fsmiasp-dataproc-user-amit/data.json'
    load_job = bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
 
    return None
def run(argv=None):
    line=''
    with beam.Pipeline(options=PipelineOptions()) as p:
        orders = (p
             | 'Read file' >> beam.io.ReadFromText('gs://fsmiaspdev-dataproc-user-amit/dataflow/test.xml'))
        new_orders = (orders
             | beam.CombineGlobally(addlines)
             | beam.Map(parse_into_dict)
        )
        new_orders | 'write' >> beam.io.WriteToText('gs://fsmiaspdev-dataproc-user-amit/dataflow/results/tobq',file_name_suffix='.txt')
        new_orders | 'to bq' >> beam.Map(addtobq)
 
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
