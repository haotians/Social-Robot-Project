function info = face_direction();
filename = 'face.jpg';
im = imread(filename);
im = imresize(im,[100,133]);

if (exist('fconv.mexa64','file') == 0 || exist('features.mexa64','file') == 0 ...
        || exist('reduce.mexa64','file')  == 0 || exist('resize.mexa64','file') == 0 ...
        || exist('shiftdt.mexa64','file')  == 0);
    compile;
end

load face_p146_small.mat;

model.thresh = -0.85
bs = detect(im,model,model.thresh);
bs = nms_face(bs,0.3);

if length(bs) == 1;
    info(1) = bs.c - 1
    info(2) = min(bs.xy(:,1));          %x0(left-top-x) point coor of the face
    info(3) = min(bs.xy(:,2));          %y0(left-top-y) point coor of the face
    info(4) = max(bs.xy(:,3));         %x1(right-bottom-x) point coor of the face
    info(5) = max(bs.xy(:,4));         %y1(right-bottom-y) point coor of the face
else
    info(1:5) = -1;
end
