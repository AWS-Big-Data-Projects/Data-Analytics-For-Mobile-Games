import pyspark

from pyspark.sql.functions import *

from pyspark.context import SparkContext

from pyspark.sql import SQLContext

from pyspark.sql.session import SparkSession

sc = SparkContext()

spark = SparkSession(sc)

df = spark.read.parquet("s3://project-pubg/death_clean/death.parquet")

df1 = spark.read.parquet("s3://project-pubg/match_clean/match.parquet")

sqlContext = SQLContext(sc)

df.createOrReplaceTempView("death")
df1.createOrReplaceTempView("match")

sqlContext.sql("create table party_size select party_size, count(party_size) from match group by party_size")

sqlContext.sql("create table map_preference select count(map) , map from death group by map")

sqlContext.sql("create table weapon_count select Weapon_name , count(Weapon_name) as count_of_weapon from death group by weapon_name order by count_of_weapon desc limit 50")

sqlContext.sql("create table killer_kills select Killer_name , count(victim_name) as no_of_kills , first(weapon_name) as weapon_name , first(killer_placement) as killer_placement from death group by killer_name order by no_of_kills desc limit 50")


sqlContext.sql("create table dist_ride_by_wining_player select player_name, player_dist_ride,player_dist_walk, team_id, team_placement from match where team_placement=1 limit 50")

sqlContext.sql("create table dist_ride_by_lossing_player select player_name, player_dist_ride,player_dist_walk, team_id, team_placement from match order by team_placement desc limit 50")

sqlContext.sql("create table squad_kill_by_team_id select team_id, avg(player_kills) avg_player_kills  , first(team_placement) as team_placement from match where party_size=4 and team_placement=1 group by team_id order by  avg_player_kills desc limit 50")



sqlContext.sql("create table final_match_weapon1 select Weapon_name  as Weapon_count, count(Weapon_name), first(killer_placement), first(victim_placement) from (select * from death where killer_placement = 1 and victim_placement = 2) as final group by Weapon_name order by Weapon_count desc limit 50")


sqlContext.sql("create table winner_data select death.weapon_name, match.team_placement, death.killer_name from death join match using(match_id) where match.team_placement = 1")

sqlContext.sql("create table bot_analysis select player_name, player_dmg, player_kills, player_dist_ride, player_dist_walk, player_survive_time from match where player_dmg = 0 and player_kills = 0 and player_dist_ride = 0 and player_dist_walk != 0 and player_survive_time > 0 order by player_survive_time limit 100")



sqlContext.sql("create table noob_analysis select player_name, player_dmg, player_kills, player_dist_ride, player_survive_time from match where player_dmg = 0 and player_kills = 0 and  player_survive_time>0 and player_dist_ride>0 order by player_survive_time limit 100")


sqlContext.sql("create table red_zone_avg_dmg select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='death.RedZoneBomb_C' group by Weapon_name")

sqlContext.sql("create table red_zone select Weapon_name , player_dmg , player_kills, player_name from death  join match using(match_id) where Weapon_name='death.RedZoneBomb_C' order by player_kills desc limit 500")

sqlContext.sql("create table blue_zone select Weapon_name , player_dmg , player_kills, player_name from death  join match using(match_id) where Weapon_name='Bluezone' order by player_kills desc limit 500")

sqlContext.sql("create table blue_zone_avg_dmg select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='Bluezone' group by Weapon_name")


sqlContext.sql("create table short_dist_weapon_avg1 select Weapon_name , avg(player_dmg) as avg_damage , avg(player_kills) as avg_death from death  join match using(match_id) where Weapon_name='Crowbar'or Weapon_name='death.WeapSawnoff_C' or Weapon_name='Crossbow'or Weapon_name='Pan' or weapon_name='punch' group by Weapon_name")


sqlContext.sql("create table max_time select time, count(player_name) as player_count, first(player_name) as player_name , first(party_size) as party_name from match group by time order by player_count desc limit 100")

sqlContext.sql("create table Air_drop_weapon select weapon_name, count(victim_name) from death where weapon_name = 'AWM' or weapon_name = 'Mk14' or weapon_name = 'M249' or weapon_name = 'Groza' or Weapon_name = 'AUG' group by weapon_name")

sqlContext.sql("create table Equivalent_to_Air_drop_weapon select weapon_name, count(victim_name) from death where weapon_name = 'Kar98k' or weapon_name = 'AKM' or weapon_name = 'M24' or weapon_name = 'UMP9' or Weapon_name = 'SCAR-L'  group by weapon_name")




