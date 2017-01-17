#ifndef __XF_VSR_H__
#define __XF_VSR_H__

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include "iostream"

#include <sys/time.h>

#include "qisr.h"
#include "msp_cmn.h"
#include "msp_errors.h"

#include <sstream>

#define SAMPLE_RATE_16K     (16000)
#define SAMPLE_RATE_8K      (8000)
#define MAX_GRAMMARID_LEN   (64)
#define MAX_PARAMS_LEN      (1024)

const char * ASR_RES_PATH        = "fo|res/asr/common.jet"; //离线语法识别资源路径
const char * GRM_BUILD_PATH      = "res/asr/GrmBuilld"; //构建离线语法识别网络生成数据保存路径
const char * GRM_FILE            = "call.bnf"; //构建离线识别语法网络所用的语法文件
const char * LEX_NAME            = "contact"; //更新离线识别语法的contact槽（语法文件为此示例中使用的call.bnf）

typedef struct _UserData {
    int     build_fini; //标识语法构建是否完成
    int     update_fini; //标识更新词典是否完成
    int     errcode; //记录语法构建或更新词典回调错误码
    char    grammar_id[MAX_GRAMMARID_LEN]; //保存语法构建返回的语法ID
}UserData;


const char *get_audio_file(void); //选择进行离线语法识别的语音文件
int build_grammar(UserData *udata); //构建离线识别语法网络
int update_lexicon(UserData *udata); //更新离线识别语法词典
int run_asr(UserData *udata); //进行离线语法识别
int run_asr(UserData *udata, const char *asr_audiof);
int run_asr(UserData *udata, const char *asr_audiof, char *rec_rslt1);
void xf_log_out();


#endif