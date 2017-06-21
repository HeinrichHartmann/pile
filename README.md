# pile

A document management tool.

Pile allows to transform a rather unstructured folder of files into a nicely organized pile of
documents:

```
2017-04-04 #S4907 #Choir List of names.pdf
2017-04-05 #EXCITE #S=5005 Notes on Data Repositories.pdf
2017-04-06 #ARAG #S=5031 #Amount=14.2EUR Invoice.pdf
```

With the following semantic fields:

- date. Every file name is prefixed with the ISO date to facilitate sorting
- tags. The syntax `#<tagname>` to categorize documents with tags.
- key-value pairs. The syntax `$<key>=value` let's us attach structured information to the document
- name. A textual description of the document

Pile provides the following features to manage documents in this form

- Normalize file names by bringing the fields in the right order
- Query the document pile for tags, key-value pairs or names
- Parse and export document metadata from filenames as CSV, JSON, sqlitedb

## Design Goals

- Work with the file system so that finder, dropbox, git, etc. can be used to manage documents
