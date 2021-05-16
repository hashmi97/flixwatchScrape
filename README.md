# flixwatchScrape tool


### Description 
Use this tool to scrape https://www.flixwatch.co/ website

### Python packages to install
`pip install requests bs4 pandas`

You can find the full list of requirements [here.](../blob/main/requirments.txt)


### Usage
To use the tool, you can just run the following command

`main.py [-h] [-v] [-l LogFile.txt] [-o Output.csv]`

- This will create two files, `LogFile.txt` which will hold log detailing what 
  countries were covered at what time and what shows were printed.
- The final dataset will be saved to `Output.csv`.
- If the `-l` and `-o` file names are not passed, by default the log will be 
  saved to `log.txt` and the dataset to `dataset.csv`.
- If the verbose option is enabled, the log file outputs will also be printed 
  to the screen in real time.
- This will take around 2 hours to generate the dataset.
### Dataset 
- the dataframe will have the following headers.


 |index|Name|Datatype|Description|
 |:---:|:---:|:---:|:---:|
 |0|Name|String|Name of the show.|
 |1|Type|String|Either tv-show or movie.|
 |2|Description|String|Short description of the synopsis.|
 |3|Genre|Comma separated values as a string|Best Genres that describe the show. There are 25 different [genres](#Genres).|
 |4|AltGenre|Comma separated values as a string|Additional Genres that can describe the show. There are more than 800 additional genres.|
 |5|StreamingCountries|Comma separated values as a string|List of the countries that include this show in their catalog.|
 |6|IMDbScore|Float|Either Nan or a float in the range (0,10).|
 |7|MetacriticScore|Float|Either a Nan or a float in the range (0, 100).|
 |8|Age|Float|Either a Nan or a float in the range (3, 18).|
 |9|FamilyFriendly|String|Either Yes or No to signify if the show is family friendly.| |10|Year|Int|The year the show was released.|
 |11|Audio|String|The language of the show.|

<a id="Genres"></a>
 ### List of available genres: 
`['Action' 'Adventure' 'Animation' 'Anime' 'Biography' 'Comedy' 'Crime'
 'Documentary' 'Drama' 'Faith' 'Family' 'Fantasy' 'Game-Show' 'Horror'
 'Music' 'Mystery' 'Reality TV' 'Romance' 'Sci-Fi' 'Sport'
 'Stand-Up Comedy' 'Talk-Show' 'Thriller' 'War' 'Western']`
