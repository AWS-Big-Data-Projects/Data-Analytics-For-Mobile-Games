# PUBG Data Anaylsis
### Introduction
Player Unknown's Battlegrounds (PUBG), is a first person shooter game where the goal is to be the last player standing. You are placed on a giant circular map that shrinks as the game goes on, and you must find weapons, armor, and other supplies in order to kill other players / teams and survive.
![Download-PUBG-Wallpaper](https://user-images.githubusercontent.com/63596869/105325185-528b3480-5bf2-11eb-9a18-fb188757eaa0.jpg)
Being outside the playable area will slowly inflict damage on players until they either die or manage to run into the playable area before all their health is lost. The game can be played in Solo, Duo or Squad mode with up to 4 players. The goal of the game is obviously to be the last one standing to get the win.
PUBG can be played both in a first and third person perspective, and this is a choice the players select in the menu while matchmaking. When it comes to the esport scene, first-person is always the choice since it’s more skill-based and doesn’t allow you to peek around corners without exposing yourself. In the beginning of each game, all the players are gathered in a lobby until the amount of players reaches  90-100, and then a 1 minute timer starts.
[Read More about PUBG](https://en.wikipedia.org/wiki/PlayerUnknown%27s_Battlegrounds)

**The Dataset**
The dataset we have taken from [Kaggle](https://www.kaggle.com/skihikingkevin/pubg-match-deaths). This dataset provide two zip files match and deaths.
##### The process of importing and unzipping the file is done in AWS EMR, by creating AWS EMR. [Read more about AWS EMR](https://aws.amazon.com/emr/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc).

The variables are described as follow:-
**Table1: Match Record data**
Variable Name | Variable Meaning | Variable Type |
--------------|------------------|---------------|
date|Start time of the game|Nominal
game_size|Site size|Discrete
match_id|Event Unique ID|Nominal
match_mode|Game Mode (First/Third Person View)|Nominal
party_size|Squad size (1 person/2 people/4 people)|Discrete
player_assists|Rescue teammates|Discrete
player_dbno|Number of times the player was knocked down|Discrete
player_dist_ride|Driving Distance|Continuous
player_dist_walk|Walking distance|Continuous
player_dmg|Injury points|Discrete
player_kills|kills|Discrete
player_name|Player Game id|Nominal
player_survive_time|Player survival time|Continuous
team_id|The player’s team number|Discrete
team_placement|The final ranking of the player’s team|Discrete

**Table2: Role death record data**
Variable Name | Variable Meaning | Variable Type |
--------------|------------------|---------------|
killed_by|Which weapon is killed|Nominal
killer_name|Killer game id|Nominal
killer_placement|The final ranking of the team where the killer is located|Discrete
killer_position_x|X coordinate of the killer when the killing behavior occurs|Continuous
killer_position_y|The Y coordinate of the killer when the killing behavior occurs|Continuous
map|Game Map (ERANGEL ISLAND/MIRAMAR DESERT)|Nominal
match_id|Event Unique ID|Nominal
time|When the kill occurs (how many seconds after the game starts)|Discrete
victim_name|The killed game id|Nominal
victim_placement|The final ranking of the team where the killer is located|Discrete
victim_position_x|X coordinate of the person being killed when the killing occurs|Continuous
victim_position_y|The Y coordinate of the killer at the time of the killing behavior|Continuous

The original data set includes about 60 million observations of match dataset and death data Set. 

**Below is the following steps how we imported the data and visualized the dataset:-**

#### 1) Upload dataset from kaggle to EMR:
 *Installing the library*
- Write the command ...>pip install kaggle
*Setting up the API token*
- Go to the kaggle website.
- Click on Your profile button on the top right and then select My Account.
- Scroll down to the API section and click on the Create New API Token button.
- It will download the file kaggle.json & Save the file at a known location on your machine.
- Move the downloaded file to a location:
```~/.kaggle/kaggle.json. ```
- If you don’t have the .kaggle folder in your home directory, you can create one using the command:
```mkdir ~/.kaggle```
- Now move the downloaded file to this location using:
```mv <location>/kaggle.json ~/.kaggle/kaggle.json```
- You need to give proper permissions to the file (since this is a hidden folder):
```chmod 600 ~/.kaggle/kaggle.json```
- The run the command as ...>
*kaggle competitions list*
- So if you find the location such as ~/.local/bin/kaggle, try running the kaggle command as:
```~/.local/bin/kaggle competitions list```




#### 2)Connect from EMR to S3:
> aws configure 
- aws_access_key_id = *write your aws access key ID from credentials
- aws_secret_access_key = *write your aws secret access key from credentials

Check if the credentials have been configured
`aws s3 ls`

**If you still get an error while reading from s3 then configure:-**
`sudo vi ~/.aws/credentials `
- After opening this credentials write your AWS account details and save `:wq`

Again check if the credentials have been configured
`aws s3 ls`

#### 3)Command for copy the data from EMR to S3:
> aws s3 cp aggregate/ s3://project-pubg/matches/ --recursive 
aws s3 cp deaths/ s3://project-pubg/deaths/ --recursive
- --recursive will travese all the directories within.
**Alternative command for copying:- 
s3-dist-cp --src [put path] here --dest [put path here]**


#### 4)Go to the pyspark on HDFS  
command....> pyspark

- Read multiple csv from S3 to spark(Here we have merged all the files in one dataframe)    

>match = spark.read.format("csv").option("header","true").option("inferSchema","true").load ("s3://project-pubg/pubg/agg_match_stats_[0-4]*.csv")

> death = spark.read.format("csv").option("header","true").option("inferSchema","true").load ("s3://project-pubg/pubg/kill_match_stats_final_[0-4]*.csv")

- Check count of rows:
> match.count()
death.count()

![11](https://user-images.githubusercontent.com/63596869/105178462-11414900-5b4e-11eb-8f3e-3ddfd5fcd651.JPG)

- Check schema
> match.printSchema()
death.printSchema()

![12](https://user-images.githubusercontent.com/63596869/105178464-130b0c80-5b4e-11eb-994a-1a3032fa1dc5.JPG)

#### 5)Clean the data and store in parquet format:
> from pyspark.sql.functions import split,regexp_replace
split_col = pyspark.sql.functions.split(df['date'], 'T')
match = df.select(split_col.getItem(0).alias('Date'),split_col.getItem(1).alias('Time'),"game_size","match_id","match_mode","party_size","player_assists","player_dbno","player_dist_ride","player_dist_walk","player_dmg","player_kills","player_name","player_survive_time","team_id","team_placement")

- Applying regex for cleaning the data.
>d= r'\\+0000$'  
b= r'\d{9}$'

>match_clean = match.select("Date",regexp_replace(match['Time'],d,'').alias('Time'),"game_size","match_id","match_mode","party_size","player_assists","player_dbno",
regexp_replace(match["player_dist_ride"],b,'').alias("player_dist_ride"),
regexp_replac(match["player_dist_walk"],b,'').alias("player_dist_walk"),"player_dmg","player_kills","player_name","player_survive_time","team_id","team_placement")
match_clean.show(5)

- Changing column name from killed_by to weapon_name for better understanding.
>death_clean = deaths.withColumnRenamed("killed_by", "Weapon_name")
death_clean.show(5)

![regex](https://user-images.githubusercontent.com/63596869/105184066-ee666300-5b54-11eb-93fd-bc1a21b1ed21.jpg)

![13](https://user-images.githubusercontent.com/63596869/105184041-e60e2800-5b54-11eb-9694-e649af8651ec.JPG)
![16](https://user-images.githubusercontent.com/63596869/105184047-e8708200-5b54-11eb-88b9-2112ae18be38.JPG)

#### 6)Save the cleaned data in S3 Bucket into parquet format.
> match_clean.write.parquet(s3://project-pubg/match_clean/match.parquet)
 death_clean.write.parquet(s3://project-pubg/death_clean/death.parquet)
 
![17](https://user-images.githubusercontent.com/63596869/105184058-ec040900-5b54-11eb-9edf-5c72df19e44b.JPG)

#### 7)Load the data from S3 to pyspark.
> df = spark.read.parquet("s3://project-pubg/death_clean/death.parquet")
df1 = spark.read.parquet("s3://project-pubg/match_clean/match.parquet")

**Creating a temporary table named death and match.**
- Using SparkSQL for creating Hive tables.

![26](https://user-images.githubusercontent.com/63596869/105185400-7ac55580-5b56-11eb-8e59-8aec5db04158.JPG)

**For creating tables and querrying in Hive, rather than explicitly creating and defining the tables we created a script file where all the queries of Hive is stored in that vi editor. To get the detailed querry code [click here](https://github.com/vinayrevankar14/Pubg-Analysis/blob/main/Pubg_Hive_Table_Creator.py)**

#### From the created tables we are now connecting to Tableau for better Visualization and understanding below are the querries with their respective visualization.  

1) >  sqlContext.sql("create table party_size select party_size, count(party_size) from match group by party_size")

![Party Size](https://user-images.githubusercontent.com/63596869/105191577-430ddc00-5b5d-11eb-8fcd-7964e0be4644.jpg)
**Above graph represents how many players are played in solo,duo and sqaud party size. It clearly Says that most players played Squad mode.**   

-------------------------------------------------------------------------------------------

2) >sqlContext.sql("create table max_time select time, count(player_name) as player_count, first(player_name) as player_name , first(party_size) as party_name from match group by time order by player_count desc limit 100")

![Rush hour of Players](https://user-images.githubusercontent.com/63596869/105191586-45703600-5b5d-11eb-9119-90d884620f39.jpg)
**Above graph represents how many players are played on which time mostly in solo, duo and squad party size. Solo mode is most played on 5:18:54**

--------------------------------------------------------------------------------------------

3) >sqlContext.sql("create table weapon_count select Weapon_name , count(Weapon_name) as count_of_weapon 
from death group by weapon_name order by count_of_weapon desc limit 50")

![Weapon Count](https://user-images.githubusercontent.com/63596869/105193995-28d4fd80-5b5f-11eb-836d-769e8fa91da0.jpg)

**Above visualization shows the most used weapons in the season of our dataset**

------------------------------------------------------------------------------------------

4) > sqlContext.sql("create table final_match_weapon1 select Weapon_name  as Weapon_count, count(Weapon_name), first(killer_placement), first(victim_placement) from (select * from death where killer_placement = 1 and victim_placement = 2) as final group by Weapon_name order by Weapon_count desc limit 50")

![FinalMatchWeapon](https://user-images.githubusercontent.com/63596869/105199792-2c6b8300-5b65-11eb-802e-17306af8829b.jpg)

**This visualization shows most weapon preffered by a palyer at the end of the match.**

----------------------------------------------------------------------------------------

5)  >sqlContext.sql("create table Air_drop_weapon select weapon_name, count(victim_name) from death where weapon_name = 'AWM' or weapon_name = 'Mk14' or weapon_name = 'M249' or weapon_name = 'Groza' or Weapon_name = 'AUG' group by weapon_name")

![Air Drop](https://user-images.githubusercontent.com/63596869/105200155-89ffcf80-5b65-11eb-841f-799f7bace166.jpg)

**It shows the kill count of air drop weapons**

----------------------------------------------------------------------------------------

6) >sqlContext.sql("create table Equivalent_to_Air_drop_weapon select weapon_name, count(victim_name) from death where weapon_name = 'Kar98k' or weapon_name = 'AKM' or weapon_name = 'M24' or weapon_name = 'UMP9' or Weapon_name = 'SCAR-L'  group by weapon_name")

![Equivalent to Air Drop](https://user-images.githubusercontent.com/63596869/105200140-866c4880-5b65-11eb-96aa-3cac6f24a150.jpg)

**It shows the kill count of equivalent air drop weapons**

-----------------------------------------------------------------------------------------

7) >sqlContext.sql("create table short_dist_weapon_avg1 select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='Crowbar'or Weapon_name='death.WeapSawnoff_C' or Weapon_name='Crossbow'or Weapon_name='Pan' or weapon_name='punch' group by Weapon_name")

![Short_dist_weapon](https://user-images.githubusercontent.com/63596869/105200151-88cea280-5b65-11eb-933b-5f91963dc33a.jpg)

**This shows the average damage and average death of short distance weapons per match**

--------------------------------------------------------------------------------------------

8) > sqlContext.sql("create table red_zone_avg_dmg select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='death.RedZoneBomb_C' group by Weapon_name")

![red zone avg](https://user-images.githubusercontent.com/63596869/105231801-71a3ab00-5b8d-11eb-8e5a-9585ec2ebeef.jpg)

**This shows the average damage and average death caused by RedZone per match**

--------------------------------------------------------------------------------------------

9) >sqlContext.sql("create table red_zone select Weapon_name , player_dmg , player_kills, player_name from death  join match using(match_id) where Weapon_name='death.RedZoneBomb_C' order by player_kills desc limit 500")

![Player Killed in RedZone and how much damage they suffer](https://user-images.githubusercontent.com/63596869/105231811-749e9b80-5b8d-11eb-8104-f0a063f0028d.jpg)

**This shows the average damage and average death caused by RedZone per match**

>sqlContext.sql("create table blue_zone select Weapon_name , player_dmg , player_kills, player_name from death  join match using(match_id) where Weapon_name='Bluezone' order by player_kills desc limit 500")

![Player Killed in BlueZone](https://user-images.githubusercontent.com/63596869/105231806-736d6e80-5b8d-11eb-8a3f-02829d884b26.jpg)

**

>sqlContext.sql("create table blue_zone_avg_dmg select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='Bluezone' group by Weapon_name")

![blue zone avg](https://user-images.githubusercontent.com/63596869/105231789-6ea8ba80-5b8d-11eb-8e6e-bbd673ac35ce.jpg)

**

> sqlContext.sql("create table bot_analysis select player_name, player_dmg, player_kills, player_dist_ride, player_dist_walk, player_survive_time from match where player_dmg = 0 and player_kills = 0 and player_dist_ride = 0 and player_dist_walk != 0 and player_survive_time > 0 order by player_survive_time limit 100")

![Bot  Analysis](https://user-images.githubusercontent.com/63596869/105232085-e545b800-5b8d-11eb-8caa-2164d11d4ad9.jpg)

**

> sqlContext.sql("create table noob_analysis select player_name, player_dmg, player_kills, player_dist_ride, player_survive_time from match where player_dmg = 0 and player_kills = 0 and  player_survive_time>0 and player_dist_ride>0 order by player_survive_time limit 100")

![noob Analysis](https://user-images.githubusercontent.com/63596869/105232090-e70f7b80-5b8d-11eb-9151-f0b151821557.jpg)

**

> sqlContext.sql("create table killer_kills select Killer_name , count(victim_name) as no_of_kills , first(weapon_name) as weapon_name , first(killer_placement) as killer_placement from death group by killer_name order by no_of_kills desc limit 50")

![Killer_kills](https://user-images.githubusercontent.com/63596869/105232588-9d736080-5b8e-11eb-8c70-a9ca5b625c79.jpg)

**

> sqlContext.sql("create table squad_kill_by_team_id select team_id, avg(player_kills) avg_player_kills  , first(team_placement) as team_placement from match where party_size=4 and team_placement=1 group by team_id order by  avg_player_kills desc limit 50")

![Squad Kill by TeamID](https://user-images.githubusercontent.com/63596869/105232681-baa82f00-5b8e-11eb-9b82-aecd91085a43.jpg)

**

> sqlContext.sql("create table dist_ride_by_wining_player select player_name, player_dist_ride,player_dist_walk, team_id, team_placement from match where team_placement=1 limit 50")

![Distance Ride by Winning Player](https://user-images.githubusercontent.com/63596869/105233598-132bfc00-5b90-11eb-9370-018a03d922f9.jpg)

**

> sqlContext.sql("create table dist_ride_by_lossing_player select player_name, player_dist_ride,player_dist_walk, team_id, team_placement from match order by team_placement desc limit 50")

![Distance Ride by Lossing Player](https://user-images.githubusercontent.com/63596869/105233607-158e5600-5b90-11eb-9383-e2a506b89a69.jpg)

**9) Check the created table are stored in hive or not.**
- hive commands 
> use default;
Show tables;
select * from death limit 5;
describe death;
-Check the data in warehouse
hdfs dfs -ls /user/hive/warehouse/death

![1](https://user-images.githubusercontent.com/63596869/105316953-9b89bb80-5be7-11eb-9ca6-70a50d499b29.jpg)

**10)Stored the .py script from EMR to S3**
> aws s3 cp /home/pubg_hive_table_creator.py s3://project-pubg/script_pubg/

**11)Reading file from S3**

> hdfs dfs -get s3://project-pubg/script_pubg/pubg_hive_table_creator.py /home/hadoop/

**12)Running the python file and creating hive tables automatically**

> spark-submit --conf spark.sql.catalogImplementation=hive pubg_hive_table_creator.py

**The above table created in Hive have been visualized in Tableau by connecting to Amazon EMR Hadoop Hive Server. The following steps to connect to Amazon EMR Hadoop Hive as follow:**
1. Open tableau
2. Go to the server option
3. Click on more & then select Amazon EMR Hadoop Hive
4. Copy EMR endpoint in server box
5. Port :10000 and type(hiveserver2)
4. Select authentication As username and give username as hadoop
5. Click on require SSL


![Untitled](https://user-images.githubusercontent.com/63596869/105317861-c3c5ea00-5be8-11eb-8a23-6d75aa689d8b.jpg)


**Automation:**
* EMR Steps- Use to invoke application without logging into instance.
* manunally  invoking spark apllication
* while creating EMR and selecting software application select desired step type.
* In our case for spark application select spark application
*       select s3 path of .py file
*       In spark-submit option insert the following command:
*       --conf spark.sql.catalogimplementation=hive 


**AWS Cloud Formation Template:**
* Create a EMR template with spark application steps.
* Save this CFT in .json format in s3.
* [Cloud Formation Template](https://github.com/vinayrevankar14/Pubg-Analysis/blob/main/CloudFornationTemplate.json).

**AWS Lambda Function:**
* Create a lambda function for triggering cloud formation template.
* Invoke the lambda function through API gateway.
* [Lambda Function](https://github.com/vinayrevankar14/Pubg-Analysis/blob/main/final_lambdaGetApi.py).

**AWS API Gateway:**
* Creating rest API and use get method.
* Link?stack-name=pubgAnalysisStack

#### Conclusion:-  From this Project we learned different AWS services and work with huge dataset and got insights from it.
**We faced some Challenges to create this project like**
1. Our dataset was huge i.e. about 18GB.
2. How to get the dataset into EMR.
3. How to store the dataset into S3.
4. Cleaning the dataset by using Spark.
5. Store the data into S3 in Parquet format.
6. How to store data directly into Hive.
7. Running Script on EMR.
8. How to add a Script to EMR step for automation..
9. How to automate the above process using Cloud Formation Template.
10. Adding EMR steps in Cloud Formation Template.
11. Creating Lambda and API Gateway.




                                            THANK YOU.....!
                                            Happy Learning












