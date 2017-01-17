// STL Header
#include <iostream>
  
// OpenCV Header
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
  
// o1. OpenNI Header
#include <OpenNI.h>
  
// n1. NiTE Header
#include <NiTE.h>
  
// namespace
using namespace std;
using namespace openni;
// using namespace nite;

FILE *file_id;
  
int track(void)
{
  file_id = fopen("limbs2.txt","w");
  if (file_id == NULL) {
    fprintf(stderr, "Can't open input file in.list!\n");
    exit(1);
  }
  fprintf(file_id,"# JOINT_HEAD JOINT_NECK JOINT_LEFT_SHOULDER \
            JOINT_RIGHT_SHOULDER JOINT_LEFT_ELBOW \
            JOINT_RIGHT_ELBOW JOINT_LEFT_HAND JOINT_RIGHT_HAND \n" );
  // o2. Initial OpenNI
  if( OpenNI::initialize() != STATUS_OK )
  {
    cerr << "OpenNI Initial Error: " 
         << OpenNI::getExtendedError() << endl;
    return -1;
  }
  
  // o3. Open Device
  Device mDevice;
  if( mDevice.open( ANY_DEVICE ) != STATUS_OK )
  {
    cerr << "Can't Open Device: " 
         << OpenNI::getExtendedError() << endl;
    return -1;
  }
  
  // o4. create depth stream
  VideoStream mDepthStream;
  mDepthStream.create( mDevice, SENSOR_DEPTH );
  // o4a. set video mode
  VideoMode mDMode;
  mDMode.setResolution( 640, 480 );
  mDMode.setFps( 30 );
  mDMode.setPixelFormat( PIXEL_FORMAT_DEPTH_1_MM );
  mDepthStream.setVideoMode( mDMode);
  
  // o5. Create color stream
  VideoStream mColorStream;
  mColorStream.create( mDevice, SENSOR_COLOR );
  // o5a. set video mode
  VideoMode mCMode;
  mCMode.setResolution( 640, 480 );
  mCMode.setFps( 30 );
  mCMode.setPixelFormat( PIXEL_FORMAT_RGB888 );
  mColorStream.setVideoMode( mCMode);
   
  // o6. image registration
  mDevice.setImageRegistrationMode( IMAGE_REGISTRATION_DEPTH_TO_COLOR );
  
  // n2. Initial NiTE
  nite::NiTE::initialize();
  
  // n3. create user tracker
  nite::UserTracker mUserTracker;
  mUserTracker.create( &mDevice );
  mUserTracker.setSkeletonSmoothingFactor( 0.1f );
  
  // create OpenCV Window
  cv::namedWindow( "User Image",  CV_WINDOW_AUTOSIZE );
  
  // p1. start
  mColorStream.start();
  mDepthStream.start();
  
  while( true )
  {
    // main loop
    // p2 - p5 ...
    // p2. prepare background
    cv::Mat cImageBGR;
    // p2a. get color frame
    VideoFrameRef mColorFrame;
    mColorStream.readFrame( &mColorFrame );
    // p2b. convert data to OpenCV format
    const cv::Mat mImageRGB( mColorFrame.getHeight(), mColorFrame.getWidth(),
                             CV_8UC3, (void*)mColorFrame.getData() );
    // p2c. convert form RGB to BGR
    cv::cvtColor( mImageRGB, cImageBGR, CV_RGB2BGR );
     
    // p3. get user frame
    nite::UserTrackerFrameRef  mUserFrame;
    mUserTracker.readFrame( &mUserFrame );
     
    // p4. get users data
    const nite::Array<nite::UserData>& aUsers = mUserFrame.getUsers();
    for( int i = 0; i < aUsers.getSize(); ++ i )
    {
      const nite::UserData& rUser = aUsers[i];
     
      // p4a. check user status
      if( rUser.isNew() )
      {
        // start tracking for new user
        mUserTracker.startSkeletonTracking( rUser.getId() );
      }
     
      if( rUser.isVisible() )
      {
        // p4b. get user skeleton
        const nite::Skeleton& rSkeleton = rUser.getSkeleton();
        if( rSkeleton.getState() == nite::SKELETON_TRACKED )
        {
          // p4c. build joints array
          nite::SkeletonJoint aJoints[15];
          aJoints[ 0] = rSkeleton.getJoint( nite::JOINT_HEAD );
          aJoints[ 1] = rSkeleton.getJoint( nite::JOINT_NECK );
          aJoints[ 2] = rSkeleton.getJoint( nite::JOINT_LEFT_SHOULDER );
          aJoints[ 3] = rSkeleton.getJoint( nite::JOINT_RIGHT_SHOULDER );
          aJoints[ 4] = rSkeleton.getJoint( nite::JOINT_LEFT_ELBOW );
          aJoints[ 5] = rSkeleton.getJoint( nite::JOINT_RIGHT_ELBOW );
          aJoints[ 6] = rSkeleton.getJoint( nite::JOINT_LEFT_HAND );
          aJoints[ 7] = rSkeleton.getJoint( nite::JOINT_RIGHT_HAND );

          aJoints[ 8] = rSkeleton.getJoint( nite::JOINT_TORSO );
          aJoints[ 9] = rSkeleton.getJoint( nite::JOINT_LEFT_HIP );
          aJoints[10] = rSkeleton.getJoint( nite::JOINT_RIGHT_HIP );
          aJoints[11] = rSkeleton.getJoint( nite::JOINT_LEFT_KNEE );
          aJoints[12] = rSkeleton.getJoint( nite::JOINT_RIGHT_KNEE );
          aJoints[13] = rSkeleton.getJoint( nite::JOINT_LEFT_FOOT );
          aJoints[14] = rSkeleton.getJoint( nite::JOINT_RIGHT_FOOT );
     
          // p4d. convert joint position to image
          cv::Point2f aPoint[15];
          for( int  s = 0; s < 15; ++ s )
          {
            const nite::Point3f& rPos = aJoints[s].getPosition();
            mUserTracker.convertJointCoordinatesToDepth( 
                                     rPos.x, rPos.y, rPos.z,
                                     &(aPoint[s].x), &(aPoint[s].y) );
          }
          if( 1 ){
            for (int s=0; s<8;s++)
            {
              const nite::Point3f& pt = aJoints[s].getPosition();
              fprintf(file_id,"%.4f %.4f %.4f ", pt.x, pt.y, pt.z);
            }
            fprintf(file_id,"\n");
          }     
          // p4e. draw line
          cv::line( cImageBGR, aPoint[ 0], aPoint[ 1], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 1], aPoint[ 2], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 1], aPoint[ 3], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 2], aPoint[ 4], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 3], aPoint[ 5], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 4], aPoint[ 6], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 5], aPoint[ 7], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 1], aPoint[ 8], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 8], aPoint[ 9], cv::Scalar( 255, 0, 0 ), 3 );
          cv::line( cImageBGR, aPoint[ 8], aPoint[10], cv::Scalar( 255, 0, 0 ), 3 );

          // p4f. draw joint
          for( int  s = 0; s < 11; ++ s )
          {
            if( aJoints[s].getPositionConfidence() > 0.5 )
              cv::circle( cImageBGR, aPoint[s], 3, cv::Scalar( 0, 0, 255 ), 2 );
            else
              cv::circle( cImageBGR, aPoint[s], 3, cv::Scalar( 0, 255, 0 ), 2 );
          }
        }
      }
    }

    // p5. show image
    cv::imshow( "User Image", cImageBGR );
        // p6. check keyboard
    if( cv::waitKey(1) == 'q' )
      break;  
  }
      
  // p7. stop
  mUserTracker.destroy();
  mColorStream.destroy();
  mDepthStream.destroy();
  mDevice.close();
  nite::NiTE::shutdown();
  OpenNI::shutdown();
  
  return 0;
}


int main( int argc, char **argv )
{
  track();
}
