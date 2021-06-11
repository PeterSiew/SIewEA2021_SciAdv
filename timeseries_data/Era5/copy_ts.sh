
input_folder="/Data/skd/scratch/ysi082/Era5_monthly"

for path in $input_folder/*/; do
	
	model=$(basename $path)
	echo $model
	mkdir $model
	cd $model
	mkdir ts
	cd ts
	cp $input_folder/$model/ts/BKSICE_monthly_anom_ts.nc ./
	cp $input_folder/$model/ts/BKSTHF_monthly_anom_ts.nc ./
	cp $input_folder/$model/ts/URALS_monthly_anom_ts.nc ./
	cp $input_folder/$model/ts/PCH50_monthly_anom_ts.nc ./
	cp $input_folder/$model/ts/NAOSLPbased_monthly_anom_ts.nc ./
	cd ../../
done

