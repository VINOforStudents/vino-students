Debugging Process
===

- **Author**: Margarita Fedulova
- **Date**: 16-06-2025
- **Version**: 0.1
- **Stage**: Draft

# Table of Contents

- [Debugging Process](#debugging-process)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)


# Introduction

In this document, a simple debugging process leveraging AI will be reviewed. The purpose of this assignment is to identify and eliminate a bug, affecting the functionality of the application.

The bug in question:
When uploading documents to databases (`Supabase` and `ChromaDB`), files undergo processing. The final process in the loop being movement to `kb/` folder. If one of the files throws an error during processing, none of the files will be moved.

This might prove problematic for the future developers working on VINO for students due to lack of clarity in the output and unfamiliarity with the project.

Methodology
- **Expert Interview**: Leverage AI to debug and eleminate and an error.

# Problem Identification

