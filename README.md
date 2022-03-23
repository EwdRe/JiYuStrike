# JiYuStrike

基于[Jiyu_udp_attack](https://github.com/ht0Ruial/Jiyu_udp_attack)项目，使用Python+Flask写的一个极域电子教室反控制系统的Web端

---
Releases里有编译好的版本，启动app.exe就可以启动服务，默认监听0.0.0.0:80

因为太菜，所以现在配置都只能去修改目录下的config.db去实现

USER表是用户，INFO是信息

USER表中POWER是权限，0表示封禁、1是普通用户、3是管理员


---

以后随缘会更新后台，因为代码能力不算很强，所以程序比较垃圾


启动时会列出数据库中的配置供选择
![sc](https://s1.ax1x.com/2022/03/23/q3nXbd.png)

登录页面，会根据配置文件中的IP计算出当前的座位
![sc](https://s1.ax1x.com/2022/03/23/q3uVVs.png)

登陆后的主页（“自杀关机”就会给自己IP发送关机指令“）
![sc](https://s1.ax1x.com/2022/03/23/q3uuGV.png)

控制靶机的页面之一（发送CMD、开关机、极域消息）
![sc](https://s1.ax1x.com/2022/03/23/q3uNPx.png)

管理员权限可以使用群控
![sc](https://s1.ax1x.com/2022/03/23/q3uBse.png)

设置中可以更改首页的公告和极域消息的权限，以及控制系统的开关
![sc](https://s1.ax1x.com/2022/03/23/q3uLWV.png)

