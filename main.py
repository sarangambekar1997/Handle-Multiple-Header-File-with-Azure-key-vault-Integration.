import get_secrets
import utils
import pyspark.sql.functions as f
import logging
from io import BytesIO

#import get_secrets
secrets = get_secrets.GetSecrets().get_secrets()

class Transformations:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def separate_headers(self, blob_name):
        try:
            if secrets is not None:
                blob_ops = utils.BlobOperations(
                    blob_name=blob_name,
                    secret_dict=secrets
                )
                df = blob_ops.download_blob()
                
                df.show()

            else:
                logging.error("Missing secrets")

            # Split the "text" column by spaces, create a new row for each word, and filter out the ones that don't start with "#"
            hashtags = (df.select(f.explode(f.split(f.col("_c0"), " ")))
                        .filter(f.col("_c0").rlike("^#"))
                        .rdd.map(lambda r: r[0])
                        .collect())

            for header in [tag[1:] for tag in hashtags]:
                # Finding Rows which contains header values only  
                df_new = df.filter(df._c0.contains(header))

                # Removing Null columns
                null_counts = df_new.select([f.count(f.when(f.col(c).isNull(), c)).alias(c) for c in df_new.columns]).collect()[0].asDict()
                to_drop = [k for k, v in null_counts.items() if v >= df_new.count()]
                df_new = df_new.drop(*to_drop)

                # Finding header row and assign it to df
                header_row = df_new.filter(df_new._c0.rlike("^#"))
                new_header = header_row.take(1)[0]

                # create a list of tuples with the old and new column names
                column_rename_list = [(col, new_header[col]) for col in df_new.columns]
                df_renamed = df_new

                # Replacing old headers with new header names
                for old_col, new_col in column_rename_list:
                    df_renamed = df_renamed.withColumnRenamed(old_col, new_col)

                # Remove duplicate row which contain same value as header
                df_new = df_renamed.filter(~(df_new[0].rlike("^#")))

                blob_report_name = header + ".csv "
                stream_file = BytesIO()
                df_new.toPandas().to_csv(stream_file)  
                file_to_blob = stream_file.getvalue()

                # Upload to Blob
                blob_ops.upload_blob(file_to_blob, blob_report_name)

        except Exception as e:
            self.logger.exception(e)

