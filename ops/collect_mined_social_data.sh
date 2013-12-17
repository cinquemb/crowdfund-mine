cd ../social-non-profit-data/
cat mined_data/* > final_mined_data/temp.json
gsed -i 's/,$//' final_mined_data/temp.json
echo 'Data Collected, Last Character Trimmed'
gsed -i '1i {"data": [' final_mined_data/temp.json
gsed -i '$a ]}' final_mined_data/temp.json
tr -d '\n' < final_mined_data/temp.json > final_mined_data/0.json
echo 'New Lines Removed'
#gzip -9 final_mined_data/0.json > final_mined_data/temp_0.json.gz
#echo 'Data Formated And Compressed'
rm final_mined_data/temp.json
#rm final_mined_data/0.json
echo 'Removed Temp File From Final Mined Data Cache'
#rm -rf mined_data/*
#echo 'Old Files Removed From Mined Data Cache'
echo 'Ready For Importing'