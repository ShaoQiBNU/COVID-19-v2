pro zonal_statistics_light

  envi_open_file, 'D:\try\class_city_id_light.tif', r_fid = fid, /invisible
  envi_file_query, fid, dims = dims
  mask = envi_get_data(fid=fid, dims=dims, pos=0)
  max_class = max(mask)
  print, max_class
  res = make_array(max_class, /float)

  envi_open_file, 'D:\try\npp_china.tif', r_fid = fid, /invisible
  envi_file_query, fid, dims = dims

  data = envi_get_data(fid=fid, dims=dims, pos=0)

  for j=1, max_class do begin
    w=where(mask eq j, count)
    print,j, count
    res[j-1] = mean(data[w])
  endfor

  write_csv, 'D:\1\city_npp.csv', res
end