# Google Sheets

## Sync overview

The Google Sheets Destination is configured to push data to a single Google Sheets spreadsheet with multiple Worksheets as streams. To replicate data to multiple spreadsheets, you can create multiple instances of the Google Sheets Destination in your Airbyte instance.
Please be aware of the [Google Spreadsheet limitations](#limitations) before you configure your airbyte data replication using Destination Google Sheets

### Output schema

Each worksheet in the selected spreadsheet will be the output as a separate source-connector stream. The data is coerced to string before the output to the spreadsheet. The nested data inside of the source connector data is normalized to the `first-level-nesting` and represented as string, this produces nested lists and objects to be a string rather than normal lists and objects, the further data processing is required if you need to analyze the data.

Airbyte only supports replicating `Grid Sheets`, which means the text raw data only could be replicated to the target spreadsheet. See the [Google Sheets API docs](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) for more info on all available sheet types.

#### Note:
* The output columns are ordered alphabetically. The output columns should not be reordered manually after the sync, this could cause the data corruption for all next syncs.
* The underlying process of record normalization is applied to avoid data corruption during the write process. This handles two scenarios:
1. UnderSetting - when record has less keys (columns) than catalog declares
2. OverSetting - when record has more keys (columns) than catalog declares
```
EXAMPLE:

- UnderSetting:
    * Catalog:
        - has 3 entities:
            [ 'id', 'key1', 'key2' ]
                        ^
    * Input record:
        - missing 1 entity, compare to catalog
            { 'id': 123,    'key2': 'value' }
                            ^
    * Result:
        - 'key1' has been added to the record, because it was declared in catalog, to keep the data structure.
            {'id': 123, 'key1': '', {'key2': 'value'} }
                            ^
- OverSetting:
    * Catalog:
        - has 3 entities:
            [ 'id', 'key1', 'key2',   ]
                                    ^
    * Input record:
        - doesn't have entity 'key1'
        - has 1 more enitity, compare to catalog 'key3'
            { 'id': 123,     ,'key2': 'value', 'key3': 'value' }
                            ^                      ^
    * Result:
        - 'key1' was added, because it expected be the part of the record, to keep the data structure
        - 'key3' was dropped, because it was not declared in catalog, to keep the data structure
            { 'id': 123, 'key1': '', 'key2': 'value',   }
                            ^                          ^
```

### Data type mapping

| Integration Type | Airbyte Type |
| :--- | :--- |
| Any Type | `string` |

### Features

| Feature | Supported?\(Yes/No\) |
| :--- | :--- |
| Ful-Refresh Overwrite | Yes |
| Ful-Refresh Append | Yes |
| Incremental Append | Yes |
| Incremental Append-Deduplicate | Yes |

### Performance considerations

At the time of writing, the [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. It is recommended that you use the same service user \(see the "Creating a service user" section below for more information on how to create one\) for no more than 3 instances of the Google Sheets Destination to ensure high transfer speeds.

### <a name="limitations"></a>Google Sheets Limitations

During the upload process and from the data storage perspective there are some limitations that should be considered beforehands:
* **Maximum of 5 Million Cells**

A Google Sheets document can have a maximum of 5 million cells. These can be in a single worksheet or in multiple sheets.
In case you already have the 5 million limit reached in fewer columns, it will not allow you to add more columns (and vice versa, i.e., if 5 million cells limit is reached with a certain number of rows, it will not allow more rows).

* **Maximum of 18,278 Columns**

At max, you can have 18,278 columns in Google Sheets in a worksheet.

* **Up to 200 Worksheets in a Spreadsheet**

You cannot create more than 200 worksheets within single spreadsheet.


## Getting Started (Airbyte Cloud Only)
To configure the connector you'll need to:

* [Authorize your Google account via OAuth](#oauth)
* [The Full URL or Spreadsheet ID you'd like to sync](#sheetlink)

### <a name="oauth"></a> Authorize your Google account via OAuth
Click on the "Sign in with Google" button and authorize via your Google account.

### <a name="sheetlink"></a>Spreadsheet Link
You will need the link of the Spreadsheet you'd like to sync. To get it, click Share button in the top right corner of Google Sheets interface, and then click Copy Link in the dialog that pops up.
These two steps are highlighted in the screenshot below:

![](../../.gitbook/assets/google_spreadsheet_url.png)


#### Future improvements:
- Handle multiple spreadsheets to split big amount of data into parts, once the main spreadsheet is full and cannot be extended more, due to [limitations](#limitations).

## Changelog

| Version | Date       | Pull Request                                               | Subject                                |
|---------|------------|------------------------------------------------------------|----------------------------------------|
| 0.1.0  | 2022-04-26 | [12135](https://github.com/airbytehq/airbyte/pull/12135)   | Initial Release                         |
