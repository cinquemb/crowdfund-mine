cd ../social-non-profit-data/
cat mined_data/* > final_mined_data/meh.json
tr -d '\n  ' < final_mined_data/meh.json > final_mined_data/temp.json
echo 'New Lines Removed'
gsed -i 's/,$//' final_mined_data/temp.json
echo 'Data Collected, Last Character Trimmed'
gsed -i -e '1i {"data_tweets": [' final_mined_data/temp.json
gsed -i -e '$a ]}' final_mined_data/temp.json
tr -d '\n' < final_mined_data/temp.json > final_mined_data/0.json
echo 'New Lines Removed Again'
#gzip -9 final_mined_data/0.json > final_mined_data/temp_0.json.gz
#echo 'Data Formated And Compressed'
rm final_mined_data/temp.json
rm final_mined_data/meh.json
#rm final_mined_data/0.json
echo 'Removed Temp File(s) From Final Mined Data Cache'
#rm -rf mined_data/*
#echo 'Old Files Removed From Mined Data Cache'
echo 'Ready For Importing'