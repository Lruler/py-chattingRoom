1.安装项目所需依赖，命令输入
pip install -r requirements.txt

2.创建数据库，一个users表，一个messages表,表结构特别简单，自己创建吧；
users：user——id(int);email(varchar);password(varchar);user_name(varchar);avatar_url(varchar)存头像路径：
message表：message_id（int）;content(varchar);create_time（timestamp；user_id（int）;

3.把query.py的数据库配置改为你自己的数据库配置

4.-运行 app.py
