
```
 _____ _____ _ _ _       
|_   _/  ___| (_) | v2.0.0a   
  | | \ `--.| |_| |_ ___ 
  | |  `--. \ | | __/ _ \
  | | /\__/ / | | ||  __/
  \_/ \____/|_|_|\__\___|
  a lightwieght timeseries library
```

## Synopsis

A lightweight timeseries library for Python 3+

## Usage

__Python3__
`import tslite3`

## Motivation

This is an update to a timeseries library that I wrote years ago. I still use it manipulating timeseries for fun an profit.

I wanted something that dealt with timeseries in an elagant scalable fashion. here are some examples:

** snap arbitre

## Installation

Download and place in the same directory as your project.

## Breaking Changes

in version 2 I'm cleaning up some cruft and introduced the following breaking changes:

1. TSlite timeseries object is now a pure timeseries, I ripped out quality flags, which really should be stored in another timeseries.
2. I standardized method names to be camelCase.
3. IO routines now disregard quality flags, you can use v1 IO methods to convert old data stores.

## Contributors

@gunn4rl

## License
[APACHE 2.0](doc/LICENSE-2.0.txt)


