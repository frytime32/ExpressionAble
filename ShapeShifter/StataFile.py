import os
import tempfile

import pandas as pd

from SSFile import SSFile


class StataFile(SSFile):

    def read_input_to_pandas(self, columnList=[], indexCol="Sample"):
        if self.isGzipped:
            tempFile = super()._gunzip_to_temp_file()
            if len(columnList)>0:
                df=pd.read_stata(tempFile.name, columns=columnList)
            else:
                df=pd.read_stata(tempFile.name)
            os.remove(tempFile.name)
            return df
        if len(columnList) > 0:
            return pd.read_stata(self.filePath, columns=columnList)
        return pd.read_stata(self.filePath)

    def export_filter_results(self, inputSSFile, columnList=[], query=None, transpose=False, includeAllColumns=False,
                              gzipResults=False, indexCol="Sample"):
        df = None
        includeIndex = False
        null = 'NA'
        query, inputSSFile, df, includeIndex = super()._prep_for_export(inputSSFile, columnList, query, transpose,
                                                                        includeAllColumns, df, includeIndex, indexCol)
        if not transpose:
            df = df.set_index(indexCol) if indexCol in df.columns else df

        self.write_to_file(df, gzipResults)

    def write_to_file(self, df, gzipResults=False, includeIndex=False, null='NA'):
        # Sometimes stata interprets columns as 'object' type which is no good (sometimes). This code may fix it?
        # However, as a result, boolean values are now converted to 1s and 0s
        type_pref = [int, float, str]
        for colname in list(df.select_dtypes(include=['object']).columns):
            for t in type_pref:
                try:
                    df[colname] = df[colname].astype(t)
                    print("Warning: True/False values may have been converted to 1/0 in output")
                except (ValueError, TypeError) as e:
                    pass

        if gzipResults:
            #write to temp file
            tempFile = tempfile.NamedTemporaryFile(delete=False)
            df.to_stata(tempFile.name, write_index=True)
            tempFile.close()
            super()._gzip_results(tempFile.name, self.filePath)
        else:
            df.to_stata(self.filePath, write_index=True)
