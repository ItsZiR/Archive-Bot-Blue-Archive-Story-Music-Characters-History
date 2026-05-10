#------------ 資料表欄位相關更新 ------------
def ost_num_query_sql(table_name:str, num:int):
    ost_num_query = '''
        SELECT *
        FROM {}
        WHERE Number = {}
        ORDER BY Number;
    '''.format(table_name, num)

    return ost_num_query

def ost_composer_tracks_query_sql(table_name:str):
    ost_composer_tracks_query = '''
        SELECT *
        FROM {}
        WHERE Composer = ?
        ORDER BY Number
    '''.format(table_name)
    
    return ost_composer_tracks_query

sql_bgm_count = '''
    SELECT BA_Music.Name, BA_Students.Memorial_Lobby_Track, COUNT(BA_Students.Memorial_Lobby_Track) as BGM_count
    FROM BA_Music
    JOIN BA_Students ON BA_Music.Number = BA_Students.Memorial_Lobby_Track
    GROUP BY BA_Students.Memorial_Lobby_Track
    ORDER BY BGM_count DESC
'''

def stu_count_sql(table_name:str):
    stu_count = '''
        SELECT COUNT(*)
        FROM {}
    '''.format(table_name)

    return stu_count

def stu_unique_count_sql(table_name:str):
    stu_unique_count = '''
        SELECT COUNT(*)
        FROM(
            SELECT DISTINCT Personal_Name, Age
            FROM {}
        )
    '''.format(table_name)

    return stu_unique_count

def stu_unique_sql(table_name:str):
    stu_unique = '''
        SELECT *
        FROM(
            SELECT DISTINCT Personal_Name, Age
            FROM {}
        )
    '''.format(table_name)

    return stu_unique

def stu_school_estimate_sql(table_name:str):
    stu_school_estimate = '''
        SELECT 
            School, 
            COUNT(*) AS total_students,
            SUM(CASE WHEN Height <= 152 THEN 1 ELSE 0 END) AS height_U152,
            ROUND(AVG(Height), 2) AS average_height,
            MAX(Height) AS max_height,
            MIN(Height) AS min_height
        FROM (
            SELECT *
            FROM {}
            WHERE id NOT in (10079, 10080, 20007, 26011)
            GROUP BY Personal_Name, Age
        )
        WHERE Height GLOB '[1][0-9][0-9]*'
        GROUP BY School
        ORDER BY average_height
    '''.format(table_name)

    return stu_school_estimate

def story_list_overall_sql(table_name:str):
    story_list_overall = '''
        SELECT *
        FROM {}
        ORDER BY Number
    '''.format(table_name)

    return story_list_overall

def story_list_type_sql(table_name:str, story_type: str):
    story_list_type = '''
        SELECT *
        FROM {}
        WHERE Type = "{}"
        ORDER BY Number
    '''.format(table_name, story_type)
    
    return story_list_type