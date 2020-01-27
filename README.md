# pile

Semantics File Names for Document Management

Pile provides a set of tools, that allow you to work files that follow some human-readable
conventions, that add semantic structure into file names. Example:


```
2017-04-04 #MChoic Member List 2017.xls
2017-04-04 #Finanzamt (Steuernummer . 1231012393).pdf
2017-04-05 #EXCITE Notes on Data Repositories (Author . Max Mustermann).pdf
2017-04-06 #ARAG #Invoive 14.2EUR.pdf
2017-02-24 Pictures Hochzeit Max+Maria Mustermann.tar.gz
```

The following elements are recognized by pile semantic filenames:

- date. ISO date strings at the beginning of the file-name are recognized as dates (`^\d\d\d\d-\d\d-\d\d `)
- extension. Extensions like `.pdf` or `.tar.gz` are recognized at the end of the filename (`([.][a-z]{1-4})*$`)
- tags. The syntax `#<tagname>` to categorize documents with tags.
- attributes. The syntax `(<key> . <value>)` let's us attach attributes as key-value pairs.

## pile-cli

The pile cli `pile` provides the following features to manage documents from the command line

- Validate existing filenames `pile `
- List documents with parsed semantic fields. `pile ls`
- Query the document pile for tags, key-value pairs or names using SQL type queries. `pile select ...`
- Parse and export document metadata from filenames as CSV, JSON, sqlitedb `pile export ...`

## pile-ui

- Import view, that helps with annotating new documents

- List view with instant-filter and preview

## Design Goals

- Seamless integration with existing tooling.
  Keep using finder, dropbox, git, etc. to manage your documents.

- Don't duplicate functionality that is covered by established tools. I.e. don't do backups or
  version control.  We create and manage semantic file names.

- Support File Systems provided by Linux, OSX and Windows. (No use of `\/:`)

- No use of characters that can interfere with command line usage (`&|`). We do allow space
  characters.
