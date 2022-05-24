
```
 _       _ _ _       
| |_ ___| (_) |_ ___ 
| __/ __| | | __/ _ \
| |_\__ \ | | ||  __/
 \__|___/_|_|\__\___| v2.0.0
 a lightwieght timeseries library
```

## Synopsis

A lightweight, performant, pure python timeseries library for Python 3+

## Usage
`import tslite`

## Motivation

This is an update to a timeseries library that I wrote years ago. I still use it to manipulating timeseries for fun an profit (literally).

I wanted something that dealt with timeseries in an elagant scalable fashion. 

## Installation

Download and place in the same directory as your project.

## Breaking Changes

In version 2 I cleaned up some cruft and introduced the following breaking changes:

1. tslite timeseries object is now a pure timeseries, I ripped out quality flags, which really should be stored in another timeseries.
2. I standardized method names to be camelCase.
3. IO routines now disregard quality flags, you can use v1 IO methods to convert old data stores.


## License
[APACHE 2.0](doc/LICENSE-2.0.txt)


