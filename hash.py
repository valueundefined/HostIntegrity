#Value Undefined - HostIntegrity

import os
import hashlib
import time
import json

def openOldHash( filename ):
    try:
        with open( filename, 'r' ) as f:
            oldFileHashes = json.load( f )
            return oldFileHashes
    except:
        print("First time running, generating save file for next time")

def main():
    ignoreDir = ["dev","proc","run","snap","sys","tmp"] # Ignore these directories
    specialCases = { "var":["lib","run"] } # Ignore the subdirectories
    outputFile = "oldHashFile.txt"
    oldFileHashes = openOldHash( outputFile )
    fileHashes = {}
    
    contents = os.listdir( "/" ) # List contents of root directory
    for f in contents: # Sort through all files/directories in root directory to log those as necessaary
        path = "/" + f
        if os.path.isdir( path ) : # If the current item is a directory
            if f in ignoreDir: # Skip directories in ignore list
                print( "Ignored", f )
                continue
            
            elif f in specialCases: # Pay special attention to special cases
                contents = os.listdir( path )
                for f2 in contents: # Sort through all files/directoriees in root directory to log/ignore as necessary
                    if f2 in specialCases[ f ]: # Skip directory in special case
                        pathSpec  = f + "/" + f2 
                        print( "Ignored", pathSpec )
                        continue
                    else: # Log all other files
                        pathSpec = f + "/" + f2
                        print( "Checking", pathSpec )
                        curPath = path + "/" + f2 # Look at subdirectory
                        for root, dirs, files in os.walk( curPath ): # Walk through other directories that are not special cases
                            for name in files:
                                try: # Attempt to Hash the file
                                    hashed = hashFile( os.path.join( root, name ) )
                                    epoch_time = int( time.time() )
                                    fileHashes[ os.path.join( root, name ) ] = { "hash":hashed, "time":epoch_time }
                                except: # If file doesn't Hash, we will ignore it
                                    pass
            
            else: # Complete normal walk of the directory
                print( "Checking", f )
                for root, dirs, files in os.walk( path ):
                    for name in files:
                        try: # Attempt to Hash the file
                            hashed = hashFile( os.path.join( root, name ) )
                            epoch_time = int( time.time() )
                            fileHashes[ os.path.join( root, name ) ] = { "hash":hashed, "time":epoch_time }
                        except: # If file doesn't Hash, we will ignore it
                            pass
    
    newFiles = []
    missingFiles = []
    modifiedFiles = []
    movedFiles = {}
    foundMove = 0
    for path in fileHashes:
        if path in oldFileHashes: # File is in the same location
            if oldFileHashes[path]['hash'] == fileHashes[path]['hash']: # File has not been modified
                del( oldFileHashes[ path ] ) # Remove after used
                continue
            else: # File has been modified
                modifiedFiles.append(path)
                del( oldFileHashes[ path ] )

        else: # File not found in current location
            for path2 in oldFileHashes:
                if fileHashes[ path ][ 'hash' ] == oldFileHashes[ path2 ][ 'hash' ]: #File is contained else where on system.
                    movedFiles[ path ] = {"newLocation": path2, "time": oldFileHashes[ path2 ][ "time"] }
                    del(oldFileHashes[ path2 ])
                    foundMove = 1
                    break
            if foundMove != 1: # newFiles
                newFiles.append(path)
            foundMove = 0

    for path in oldFileHashes:
        missingFiles.append(path)


    print( "These new files were found on the system:" )
    for path in newFiles:
        print(path)

    print( "These files were missing from the system:" )
    for path in missingFiles:
        print(path)

    print( "These files were modified on the system:" )
    for path in modifiedFiles:
        print(path)

    print( "These files were moved on the system:" )
    for path in movedFiles:
        time_format = time.strftime( '%A, %B %-d, %Y %H:%M:%S', time.localtime(movedFiles[path]["time"]))
        string = path + " => " + movedFiles[path]["newLocation"] + " seen before on " + time_format
        print( string )

    writeNewHash( outputFile, fileHashes )
    return 0

def writeNewHash( filename, fileHashDict ):
    with open( filename, 'w' ) as f:
        f.write( json.dumps( fileHashDict ) )


def openOldHash( filename ):
    try:
        with open( filename, 'r' ) as f:
            oldFileHashes = json.load( f )
            return oldFileHashes
    except:
        print("First time running, generating save file for next time")
        return {} # Return blank dictionary if no file exists

def hashFile(filename): # Function referenced from https://www.programiz.com/python-programming/examples/hash-file
    h = hashlib.sha256()
    with open( filename, 'rb' ) as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read( 1024 )
            h.update( chunk )
    
    return h.hexdigest()
    
if __name__=="__main__":
    main()
