## Final Analysis of the Data 

The Makefile contains recipes to perform the final analysis. 

Please note that to perform the final analysis, you will need to download the 
data for analysis. Please go to the `project-alpha/data` directory and call 
`make data` and see its README for more information. 

- `make data`: Performs the all final data analysis that generates data files,
which are saved to the `data` subdirectory. Approximately 14 GB of data is
created by this command.
- `make images`: Performs all the final data analysis that generates images, 
which are saved to `project-alpha/images`. This includes all figures required 
for the report and slides. For convenience, images required for the report and 
slides are also cached in this directory. 

- `make all`: Performs all final data analysis, including final supplementary 
data analysis and generating all figures required for the report and slides. 
Many large data files are created from this command. 

- `make clean`: Removes all extra files generated when compiling code. Does 
this recursively for all subdirectories. 

Additional documentation and information on the subdirectories can be found in 
their respective READMEs. 
 
- `data`: Stores all data generated by final analysis. 
- `data_scripts`: Scripts to run all final analysis and supplementary final 
that generate data files. 
- `image_scripts`: Scripts to run all final analysis and supplementary final 
work that generate images.
