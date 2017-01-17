// OpenNI Header
#include <XnCppWrapper.h>

// link OpenNI library
// #pragma comment( lib, "OpenNI.lib" )

// OpenCV Header
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

// Link OpenCV Library
// #ifdef _DEBUG
//   #pragma comment( lib, "opencv_core242d.lib" )
//   #pragma comment( lib, "opencv_highgui242d.lib" )
//   #pragma comment( lib, "opencv_imgproc242d.lib" )
// #else
//   #pragma comment( lib, "opencv_core242.lib" )
//   #pragma comment( lib, "opencv_highgui242.lib" )
//   #pragma comment( lib, "opencv_imgproc242.lib" )
// #endif

// main function
int main( int argc, char** argv )
{
  // 1a. initial OpenNI
  xn::Context xContext;
  xContext.Init();

  // 1b. create depth generator
  xn::DepthGenerator xDepth;
  xDepth.Create( xContext );

  // 1c. create image generator
  xn::ImageGenerator xImage;
  xImage.Create( xContext );

  // 1d. set alternative view point
  xDepth.GetAlternativeViewPointCap().SetViewPoint( xImage );

  // 2. create OpenCV Windows
  cv::namedWindow( "Depth Image", CV_WINDOW_AUTOSIZE );
  cv::namedWindow( "Color Image", CV_WINDOW_AUTOSIZE );
  cv::namedWindow( "Depth Edge", CV_WINDOW_AUTOSIZE );
  cv::namedWindow( "Color Edge", CV_WINDOW_AUTOSIZE );

  // 3. start OpenNI
  xContext.StartGeneratingAll();

  // main loop
  while( true )
  {
    // 4. update data
    xContext.WaitAndUpdateAll();

    // 5. get image data
    {
      xn::ImageMetaData xColorData;
      xImage.GetMetaData( xColorData );

      // 5a. convert to OpenCV form
      cv::Mat cColorImg( xColorData.FullYRes(), xColorData.FullXRes(),
                         CV_8UC3, (void*)xColorData.Data() );

      // 5b. convert from RGB to BGR
      cv::Mat cBGRImg;
      cv::cvtColor( cColorImg, cBGRImg, CV_RGB2BGR );
      cv::imshow( "Color Image", cBGRImg );

      // 5c. convert to signle channel and do edge detection
      cv::Mat cColorEdge;
      cv::cvtColor( cColorImg, cBGRImg, CV_RGB2GRAY );
      cv::Canny( cBGRImg, cColorEdge, 5, 100 );
      cv::imshow( "Color Edge", cColorEdge );
    }

    // 6. get depth data
    {
      xn::DepthMetaData xDepthData;
      xDepth.GetMetaData( xDepthData );

      // 6a. convert to OpenCV form
      cv::Mat cDepthImg( xDepthData.FullYRes(), xDepthData.FullXRes(),
                         CV_16UC1, (void*)xDepthData.Data() );

      // 6b. convert to 8 bit
      cv::Mat c8BitDepth;
      cDepthImg.convertTo( c8BitDepth, CV_8U, 255.0 / 7000 );
      cv::imshow( "Depth Image", c8BitDepth );

      // 6c. convert to 8bit, and do edge detection
      cv::Mat CDepthEdge;
      cv::Canny( c8BitDepth, CDepthEdge, 5, 100 );
      cv::imshow( "Depth Edge", CDepthEdge );
    }

    cv::waitKey( 1 );
  }
}
