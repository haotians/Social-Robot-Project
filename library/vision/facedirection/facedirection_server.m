disp('start server')
com_no = 8001;
com = tcpip('localhost',com_no,'NetworkRole','server');
clear com_no;
set(com,'InputBufferSize',1);
set(com, 'Terminator', 1);
fopen(com);

while 1
    try
        command = fscanf(com);
        if strcmp(command,'1') == 1
            info = face_direction();
            fwrite(com,num2str(info+112));
        elseif strcmp(command,'2') == 1
            break;
        end
    catch
        disp('error');
    end
end

pause(2)
fclose(com);
delete(com);
disp('finish');
exit;