pro zonal_statistics

  envi_open_file, 'D:\1\class_city_id.tif', r_fid = fid, /invisible
  envi_file_query, fid, dims = dims
  mask = envi_get_data(fid=fid, dims=dims, pos=0)
  max_class = max(mask)
  
  file = file_search('D:\try2\', '*.tif', count=count)
  s = sort(file)
  
  res = make_array(count, max_class, /float)
  header = make_array(count, /string)

  for i=0, count-1 do begin
    print, file[i]
    
    filename = strsplit(file[i], '\', /extract)
    filename = strsplit(filename[-1], '.', /extract)
    header[i]=filename[0]
    
    envi_open_file, file[i], r_fid = fid, /invisible
    envi_file_query, fid, dims = dims
    
    data = envi_get_data(fid=fid, dims=dims, pos=0)
    
    for j=1, max_class do begin
      w=where(mask eq j, count)
      if count gt 0 then begin
        res[i, j-1] = mean(data[w])
      endif else begin
        print, j
        res[i, j-1] = 0
      endelse
    endfor
  endfor
  
  write_csv, 'D:\1\city_t2m.csv', res, header=header
end