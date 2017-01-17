
#include <stdio.h>
#include <string.h>    //strlen
#include <stdlib.h>    //strlen
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write 
#include <pthread.h> //for threading , link with lpthread

#include "xf_vsr.h"

UserData asr_data;

#define BUF_SOCKET_MSG 4096
 
void *connection_handler(void *);
int vsr_server(); 

int vsr_server()
{
    int socket_desc , new_socket , c , *new_sock;
    struct sockaddr_in server , client;
    char *message;
     
    //Create socket
    socket_desc = socket(AF_INET , SOCK_STREAM , 0);
    if (socket_desc == -1)
    {
        printf("Could not create socket");
        exit(1);
    }
     
    //Prepare the sockaddr_in structure
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons( 8888 );
     
    //Bind
    if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
    {
        puts("bind failed");
        return 1;
    }
    puts("bind done");
     
    //Listen
    listen(socket_desc , 3);
     
    //Accept and incoming connection
    puts("Waiting for incoming connections...");
    c = sizeof(struct sockaddr_in);
    while( (new_socket = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c)) )
    {
        puts("Connection accepted");
         
        //Reply to the client
        message = "Hello Client , I have received your connection. And now I will assign a handler for you\n";
        // write(new_socket , message , strlen(message));
         
        pthread_t sniffer_thread;
        new_sock = (int *) malloc(1);
        *new_sock = new_socket;
         
        if( pthread_create( &sniffer_thread , NULL ,  connection_handler , (void*) new_sock) < 0)
        {
            perror("could not create thread");
            return 1;
        }
         
        //Now join the thread , so that we dont terminate before the thread
        //pthread_join( sniffer_thread , NULL);
        puts("Handler assigned");
    }
     
    if (new_socket<0)
    {
        perror("accept failed");
        return 1;
    }
     
    return 0;
}
 
/*
 * This will handle connection for each client
 * */

void *connection_handler(void *socket_desc)
{
    //Get the socket descriptor
    int sock = *(int*)socket_desc;
    int read_size;
    char *message , client_message[2000];
     
    //Send some messages to the client
    message = "Connection established\n";
    // puts(message);
    // write(sock , message , strlen(message));
     
     
    //Receive a message from client
    while( (read_size = recv(sock , client_message , 2000 , 0)) > 0 )
    {
        //Send the message back to client
        // write(sock , client_message , strlen(client_message));
        puts(client_message);
        std::string str1 = "vsr";
        if (str1.compare(client_message) == 0){
            const char *asr_audiof = "wav/out.wav";
            printf("%s\n", asr_audiof);
            char *rec_rslt = (char*)malloc(sizeof(char)*BUF_SOCKET_MSG);
            run_asr(&asr_data, asr_audiof, rec_rslt);
            write(sock , rec_rslt , strlen(rec_rslt));
            free(rec_rslt);
            break;
         }
    }
     
    if(read_size == 0)
    {
        puts("Client disconnected");
        fflush(stdout);
    }
    else if(read_size == -1)
    {
        perror("recv failed");
    }
         
    //Free the socket pointer
    free(socket_desc);
     
    return 0;
}


int build_grm_cb(int ecode, const char *info, void *udata)
{
    UserData *grm_data = (UserData *)udata;

    if (NULL != grm_data) {
        grm_data->build_fini = 1;
        grm_data->errcode = ecode;
    }

    if (MSP_SUCCESS == ecode && NULL != info) {
        printf("构建语法成功！ 语法ID:%s\n", info);
        if (NULL != grm_data)
            snprintf(grm_data->grammar_id, MAX_GRAMMARID_LEN - 1, info);
    }
    else
        printf("构建语法失败！%d\n", ecode);

    return 0;
}

int build_grammar(UserData *udata)
{
    FILE *grm_file                           = NULL;
    char *grm_content                        = NULL;
    unsigned int grm_cnt_len                 = 0;
    char grm_build_params[MAX_PARAMS_LEN]    = {NULL};
    int ret                                  = 0;

    grm_file = fopen(GRM_FILE, "rb");   
    if(NULL == grm_file) {
        printf("打开\"%s\"文件失败！[%s]\n", GRM_FILE, strerror(errno));
        return -1; 
    }

    fseek(grm_file, 0, SEEK_END);
    grm_cnt_len = ftell(grm_file);
    fseek(grm_file, 0, SEEK_SET);

    grm_content = (char *)malloc(grm_cnt_len + 1);
    if (NULL == grm_content)
    {
        printf("内存分配失败!\n");
        fclose(grm_file);
        grm_file = NULL;
        return -1;
    }
    fread((void*)grm_content, 1, grm_cnt_len, grm_file);
    grm_content[grm_cnt_len] = '\0';
    fclose(grm_file);
    grm_file = NULL;

    snprintf(grm_build_params, MAX_PARAMS_LEN - 1, 
        "engine_type = local, \
        asr_res_path = %s, sample_rate = %d, \
        grm_build_path = %s, ",
        ASR_RES_PATH,
        SAMPLE_RATE_16K,
        GRM_BUILD_PATH
        );
    ret = QISRBuildGrammar("bnf", grm_content, grm_cnt_len, grm_build_params, build_grm_cb, udata);

    free(grm_content);
    grm_content = NULL;

    return ret;
}

int update_lex_cb(int ecode, const char *info, void *udata)
{
    UserData *lex_data = (UserData *)udata;

    if (NULL != lex_data) {
        lex_data->update_fini = 1;
        lex_data->errcode = ecode;
    }

    if (MSP_SUCCESS == ecode)
        printf("更新词典成功！\n");
    else
        printf("更新词典失败！%d\n", ecode);

    return 0;
}

int update_lexicon(UserData *udata)
{
    const char *lex_content                   = "丁伟\n黄辣椒";
    unsigned int lex_cnt_len                  = strlen(lex_content);
    char update_lex_params[MAX_PARAMS_LEN]    = {NULL}; 

    snprintf(update_lex_params, MAX_PARAMS_LEN - 1, 
        "engine_type = local, text_encoding = utf-8, \
        asr_res_path = %s, sample_rate = %d, \
        grm_build_path = %s, grammar_list = %s, ",
        ASR_RES_PATH,
        SAMPLE_RATE_16K,
        GRM_BUILD_PATH,
        udata->grammar_id);
    return QISRUpdateLexicon(LEX_NAME, lex_content, lex_cnt_len, update_lex_params, update_lex_cb, udata);
}

int run_asr(UserData *udata){
    const char *asr_audiof = "wav/out.wav";
    return run_asr(udata, asr_audiof);

}

int run_asr(UserData *udata, const char *asr_audiof){
    char *rec_rslt;
    rec_rslt = (char*)malloc(sizeof(char)*4096);
    int status;
    status = run_asr(udata, asr_audiof, rec_rslt);
    free(rec_rslt);
    return status;
}

int run_asr(UserData *udata, const char *asr_audiof, char *rec_rslt1)
{
    char asr_params[MAX_PARAMS_LEN]    = {NULL};
    const char *rec_rslt               = NULL;
    const char *session_id             = NULL;
    // const char *asr_audiof             = NULL;
    FILE *f_pcm                        = NULL;
    char *pcm_data                     = NULL;
    long pcm_count                     = 0;
    long pcm_size                      = 0;
    int last_audio                     = 0;
    int aud_stat                       = MSP_AUDIO_SAMPLE_CONTINUE;
    int ep_status                      = MSP_EP_LOOKING_FOR_SPEECH;
    int rec_status                     = MSP_REC_STATUS_INCOMPLETE;
    int rss_status                     = MSP_REC_STATUS_INCOMPLETE;
    int errcode                        = -1;

    struct timeval t1, t2;
    int millis1; 
    gettimeofday(&t1, NULL);


    f_pcm = fopen(asr_audiof, "rb");
    if (NULL == f_pcm) {
        printf("打开\"%s\"失败！[%s]\n", f_pcm, strerror(errno));
        goto run_error;
    }
    fseek(f_pcm, 0, SEEK_END);
    pcm_size = ftell(f_pcm);
    fseek(f_pcm, 0, SEEK_SET);
    pcm_data = (char *)malloc(pcm_size);
    if (NULL == pcm_data)
        goto run_error;
    fread((void *)pcm_data, pcm_size, 1, f_pcm);
    fclose(f_pcm);
    f_pcm = NULL;

    //离线语法识别参数设置
    snprintf(asr_params, MAX_PARAMS_LEN - 1, 
        "engine_type = local, \
        asr_res_path = %s, sample_rate = %d, \
        grm_build_path = %s, local_grammar = %s, \
        result_type = xml, result_encoding = utf-8, ",
        ASR_RES_PATH,
        SAMPLE_RATE_16K,
        GRM_BUILD_PATH,
        udata->grammar_id
        );
    session_id = QISRSessionBegin(NULL, asr_params, &errcode);
    if (NULL == session_id)
        goto run_error;
    printf("开始识别...\n");

    while (1) {
        unsigned int len = 6400;

        if (pcm_size < 12800) {
            len = pcm_size;
            last_audio = 1;
        }

        aud_stat = MSP_AUDIO_SAMPLE_CONTINUE;

        if (0 == pcm_count)
            aud_stat = MSP_AUDIO_SAMPLE_FIRST;

        if (len <= 0)
            break;

        printf(">");
        fflush(stdout);
        errcode = QISRAudioWrite(session_id, (const void *)&pcm_data[pcm_count], len, aud_stat, &ep_status, &rec_status);
        if (MSP_SUCCESS != errcode)
            goto run_error;

        pcm_count += (long)len;
        pcm_size -= (long)len;

        //检测到音频结束
        if (MSP_EP_AFTER_SPEECH == ep_status)
            break;

        usleep(20 * 1000); //模拟人说话时间间隙
    }
    //主动点击音频结束
    QISRAudioWrite(session_id, (const void *)NULL, 0, MSP_AUDIO_SAMPLE_LAST, &ep_status, &rec_status);

    free(pcm_data);
    pcm_data = NULL;

    gettimeofday(&t2, NULL);
    
    millis1 = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;

    printf("# %d m seconds difference\n", millis1);

    //获取识别结果
    while (MSP_REC_STATUS_COMPLETE != rss_status && MSP_SUCCESS == errcode) {
        rec_rslt = QISRGetResult(session_id, &rss_status, 0, &errcode);
        printf(">");
        usleep(5 * 1000);
    }
    printf("\n识别结束：\n");

    gettimeofday(&t2, NULL);   
    millis1 = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
    printf("# %d m seconds difference\n", millis1);

    printf("=============================================================\n");
    if (NULL != rec_rslt){

        printf("%s\n", rec_rslt);
        strcpy(rec_rslt1, rec_rslt);
    }

    else{
        printf("没有识别结果！\n");
        rec_rslt = "没有识别结果！\n";
        strcpy(rec_rslt1, rec_rslt);
    }
    printf("=============================================================\n");

    QISRSessionEnd(session_id, NULL);
    return errcode;

run_error:
    if (NULL != pcm_data) {
        free(pcm_data);
        pcm_data = NULL;
    }
    if (NULL != f_pcm) {
        fclose(f_pcm);
        f_pcm = NULL;
    }

    QISRSessionEnd(session_id, NULL);
    return errcode;
}

int main(int argc, char* argv[])
{
    const char *login_config    = "appid = 56a77064"; //登录参数

    // UserData asr_data; 
    int ret                     = 0 ;
    char c;

    // path for temp wav file
    char* file_audio = "wav/out.wav";

    // first time recognition, must be recognized
    const char *asr_audiof = "../../bin/wav/first_time.wav";

    struct timeval t1, t2;
    int millis1; 
    gettimeofday(&t1, NULL);

    if (argc >= 2){
        file_audio = argv[1];
        printf("audio file name %s\n", file_audio);
    }

    ret = MSPLogin(NULL, NULL, login_config); //第一个参数为用户名，第二个参数为密码，传NULL即可，第三个参数是登录参数
    if (MSP_SUCCESS != ret) {
        printf("登录失败：%d\n", ret);
        xf_log_out();
        return 0;
    }

    memset(&asr_data, 0, sizeof(UserData));
    printf("构建离线识别语法网络...\n");
    ret = build_grammar(&asr_data);  //第一次使用某语法进行识别，需要先构建语法网络，获取语法ID，之后使用此语法进行识别，无需再次构建
    if (MSP_SUCCESS != ret) {
        printf("构建语法调用失败！\n");
        xf_log_out();
        return 0;
    }
    while (1 != asr_data.build_fini)
        usleep(100 * 1000);
    if (MSP_SUCCESS != asr_data.errcode)
    {
        xf_log_out();
        return 0;
    }
    printf("离线识别语法网络构建完成，开始识别...\n");   
    // ret = run_asr(&asr_data);
    
    printf("%s\n", asr_audiof);
    char *rec_rslt = (char*)malloc(sizeof(char)*BUF_SOCKET_MSG);
    run_asr(&asr_data, asr_audiof, rec_rslt);




    if (MSP_SUCCESS != ret) {
        printf("离线语法识别出错: %d \n", ret);
        xf_log_out();
        return 0;
    }

    // ret = run_asr(&asr_data);
    gettimeofday(&t2, NULL);
    millis1 = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
    printf("$ First VSR: %d m seconds difference\n", millis1);

    printf("更新离线语法词典...\n");
    ret = update_lexicon(&asr_data);  //当语法词典槽中的词条需要更新时，调用QISRUpdateLexicon接口完成更新
    if (MSP_SUCCESS != ret) {
        printf("更新词典调用失败！\n");
        xf_log_out();
        return 0;
    }
    while (1 != asr_data.update_fini)
        usleep(100 * 1000);
    if (MSP_SUCCESS != asr_data.errcode)
    {
        xf_log_out();
        return 0;
    }
    printf("更新离线语法词典完成，开始识别...\n");

    gettimeofday(&t2, NULL);
    millis1 = (t2.tv_sec - t1.tv_sec) * 1000 + (t2.tv_usec - t1.tv_usec)/1000;
    printf("$ First VSR: %d m seconds difference\n", millis1);

    ret = run_asr(&asr_data);
    if (MSP_SUCCESS != ret) {
        printf("离线语法识别出错: %d \n", ret);
        xf_log_out();
        return 0;
    }
    // ret = run_asr(&asr_data);
    vsr_server();

    MSPLogout();
    printf("请按任意键退出...\n");
    getchar();
    return 0;
}

void xf_log_out(){
    MSPLogout();
    printf("请按任意键退出...\n");
    getchar();
}




