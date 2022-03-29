# mini_rsync

## NAME
```
       mrsync - minimalistic version of rsync
```
## SYNOPSIS
```
       mrsync [OPTION]... SRC [SRC]... DEST

       mrsync [OPTION]... SRC [SRC]... [USER@]HOST:DEST

       mrsync [OPTION]... SRC [SRC]... [USER@]HOST::DEST

       mrsync [OPTION]... SRC

       mrsync [OPTION]... [USER@]HOST:SRC [DEST]

       mrsync [OPTION]... [USER@]HOST::SRC [DEST]
```
## DESCRIPTION
```
       mrsync is a program that behaves in much the same way that rsync does, but
       has less options. 
```
## GENERAL
```
       mrsync copies files either to or from a remote host, or locally  on  the
       current  host  (it  does  not  support copying files between two remote
       hosts).

       There are two different ways for mrsync  to  contact  a  remote  system:
       using  ssh or contacting an mrsync daemon directly via TCP.  The  
       remote-shell  transport is used whenever the source or destination path 
       contains a single colon (:) separator after a host specification.
       Contacting  an  mrsync daemon directly happens when the source or 
       destination path contains a double colon (::) separator after a host 
       specification.
       
       As a special case, if a single source arg is specified without a desti-
       nation, the files are listed in an output format similar to "ls -l".

       As expected, if neither the source or destination path specify a remote
       host, the copy occurs locally (see also the --list-only option).
```

