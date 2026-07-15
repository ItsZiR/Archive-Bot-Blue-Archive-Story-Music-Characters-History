SELECT Personal_Name, Released_day
FROM BA_Students
WHERE NOT Type = 'Collab' AND NOT Family_Name = ""
GROUP BY Personal_Name
HAVING COUNT(*) = 1
ORDER BY Released_day