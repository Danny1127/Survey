import streamlit as st
import sqlite3, json

st.set_page_config(page_title="环境经济学科研入门调查", layout="wide")

# ---------- 数据库 ----------
def init_db():
    conn = sqlite3.connect("survey.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS survey(
        student_id TEXT, nickname TEXT, part TEXT, data TEXT,
        PRIMARY KEY(student_id, nickname, part))""")
    conn.commit(); conn.close()

def save_part(sid, nick, part, data):
    conn = sqlite3.connect("survey.db")
    conn.execute("INSERT OR REPLACE INTO survey VALUES(?,?,?,?)",
                 (sid, nick, part, json.dumps(data, ensure_ascii=False)))
    conn.commit(); conn.close()

def load_all(sid, nick):
    conn = sqlite3.connect("survey.db")
    rows = conn.execute("SELECT part, data FROM survey WHERE student_id=? AND nickname=?",
                        (sid, nick)).fetchall()
    conn.close()
    return {p: json.loads(d) for p, d in rows}

init_db()
if "answers" not in st.session_state:
    st.session_state.answers = {}

def idx(options, val):
    return options.index(val) if val in options else 0

# ---------- 侧边栏：身份与读取 ----------
st.sidebar.header("身份信息")
sid = st.sidebar.text_input("学号")
nick = st.sidebar.text_input("昵称")
if st.sidebar.button("读取已填内容"):
    if sid and nick:
        st.session_state.answers = load_all(sid, nick)
        st.sidebar.success("已读取，可切换 Tab 修改")
        st.rerun()
    else:
        st.sidebar.warning("请输入学号和昵称")

st.title("环境经济学科研入门调查问卷")

tabs = st.tabs(["基本信息","文献检索","AI使用","问题凝练","数据检索",
                "前沿热点","自选话题","困难与解决","总体自评"])

# ---------- 1 基本信息 ----------
with tabs[0]:
    part = "basic"; ans = st.session_state.answers.get(part, {})
    opts1 = ["大二","大三","大四","研一","其他"]
    opts2 = ["经济学类","环境科学/工程类","管理学类","其他"]
    opts3 = ["从未参加","参加过但打杂","参加过并负责部分工作","主持过完整项目"]
    grade = st.selectbox("年级", opts1, idx(opts1, ans.get("grade","大二")))
    major = st.selectbox("专业背景", opts2, idx(opts2, ans.get("major","经济学类")))
    exp = st.selectbox("科研经历", opts3, idx(opts3, ans.get("exp","从未参加")))
    if st.button("保存本部分", key="save_basic"):
        if not sid or not nick: st.warning("请先填写学号和昵称")
        else:
            data = {"grade":grade,"major":major,"exp":exp}
            save_part(sid,nick,part,data); st.session_state.answers[part]=data
            st.success("已保存")

# ---------- 2 文献检索 ----------
with tabs[1]:
    part = "lit"; ans = st.session_state.answers.get(part, {})
    tools = st.multiselect("使用过的学术检索工具",
        ["Web of Science","Scopus","CNKI","Google Scholar","EconLit","JSTOR","百度学术","其他"],
        default=ans.get("tools",[]))
    kw = st.text_input("检索“碳交易政策对企业绿色创新的影响”的关键词（至少3个）", ans.get("kw",""))
    st.markdown("**自评文献检索能力（1=完全不会，5=非常熟练）**")
    b1 = st.slider("布尔逻辑组合关键词",1,5,ans.get("b1",3))
    b2 = st.slider("引文追踪",1,5,ans.get("b2",3))
    b3 = st.slider("文献管理工具",1,5,ans.get("b3",3))
    if st.button("保存本部分", key="save_lit"):
        data = {"tools":tools,"kw":kw,"b1":b1,"b2":b2,"b3":b3}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 3 AI使用 ----------
with tabs[2]:
    part = "ai"; ans = st.session_state.answers.get(part, {})
    ai_tools = st.multiselect("使用过的AI工具",
        ["ChatGPT","Claude","Kimi","通义千问","文心一言","Consensus","Elicit","Scite","其他","从未使用"],
        default=ans.get("ai_tools",[]))
    ai_use = st.multiselect("用AI做过哪些科研相关的事",
        ["解释概念","润色文字","生成文献综述","查找文献","生成代码","分析数据","翻译","选题讨论","其他"],
        default=ans.get("ai_use",[]))
    ethic = st.text_area("学术研究中使用AI最需要注意的问题", ans.get("ethic",""))
    if st.button("保存本部分", key="save_ai"):
        data = {"ai_tools":ai_tools,"ai_use":ai_use,"ethic":ethic}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 4 问题凝练 ----------
with tabs[3]:
    part = "question"; ans = st.session_state.answers.get(part, {})
    qs = ["A. 中国应该怎样实现碳中和？","B. 碳交易试点政策是否促进了试点地区企业的绿色创新？",
          "C. 环境经济学研究综述","D. 气候变化与经济发展"]
    order = st.multiselect("请按“好研究问题”程度从高到低依次选择（第一个为最好）", qs,
                           default=ans.get("order",[]))
    worst = st.text_area("对排序最低分的问题，指出缺少什么要素、需补齐什么内容才是好研究问题",
                         ans.get("worst",""))
    new_q = st.text_area("就“新能源汽车补贴退坡”写出一个可研究的学术问题", ans.get("new_q",""))
    if st.button("保存本部分", key="save_question"):
        data = {"order":order,"worst":worst,"new_q":new_q}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 5 数据检索 ----------
with tabs[4]:
    part = "data"; ans = st.session_state.answers.get(part, {})
    dbs = st.multiselect("听说过或使用过的数据来源",
        ["国家统计局","CEADs","CNRDS","知网社会科学数据平台","Wind","CSMAR",
         "中科院资源环境科学数据中心","国家冰川冻土沙漠科学数据中心",
         "PubMed/Web of Science","生态环境部监测数据","其他"],
        default=ans.get("dbs",[]))
    st.markdown("**为以下研究问题匹配最合适的数据来源**")
    m1 = st.selectbox("1. 各省碳排放强度与产业结构", ["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], idx(["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], ans.get("m1","B. 省级统计+CEADs")))
    m2 = st.selectbox("2. 县域生态补偿转移支付是否提升森林覆盖率", ["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], idx(["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], ans.get("m2","A. 县域统计+遥感+转移支付")))
    m3 = st.selectbox("3. 绿色信贷是否促进制造业绿色专利申请", ["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], idx(["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], ans.get("m3","C. 上市公司+绿色专利+绿色信贷")))
    m4 = st.selectbox("4. 青藏高原水体微塑料与旅游活动强度", ["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], idx(["A. 县域统计+遥感+转移支付","B. 省级统计+CEADs","C. 上市公司+绿色专利+绿色信贷","D. 微塑料观测+旅游统计"], ans.get("m4","D. 微塑料观测+旅游统计")))
    after = st.text_area("找到数据后还需做哪些工作才能用于科研分析？", ans.get("after",""))
    clean_tools = st.multiselect("使用过的数据清洗/分析工具",
        ["Excel","Stata","R","Python(pandas)","SPSS","SQL","NVivo","其他"],
        default=ans.get("clean_tools",[]))
    hard = st.text_area("你认为获取数据最大的困难是什么？", ans.get("hard",""))
    if st.button("保存本部分", key="save_data"):
        data = {"dbs":dbs,"m1":m1,"m2":m2,"m3":m3,"m4":m4,"after":after,
                "clean_tools":clean_tools,"hard":hard}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 6 前沿热点（打分矩阵） ----------
with tabs[5]:
    part = "hot"; ans = st.session_state.answers.get(part, {})
    concepts = ["碳市场","ESG","绿色金融","气候风险","环境规制与竞争力",
                "生态补偿","循环经济","公正转型"]
    scores = {}
    st.markdown("**请对每个概念按了解程度打分（1=仅听说过名词，5=能说出核心争议和代表性研究）**")
    for c in concepts:
        scores[c] = st.slider(c, 1, 5, ans.get("scores",{}).get(c,1))
    if st.button("保存本部分", key="save_hot"):
        data = {"scores":scores}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 7 自选话题 ----------
with tabs[6]:
    part = "topic"; ans = st.session_state.answers.get(part, {})
    t1 = st.text_input("话题名称", ans.get("t1",""))
    t2 = st.text_area("为什么选它", ans.get("t2",""))
    t3 = st.text_area("打算怎么研究（数据、方法等）", ans.get("t3",""))
    t4 = st.text_input("可能遇到的最大困难", ans.get("t4",""))
    if st.button("保存本部分", key="save_topic"):
        data = {"t1":t1,"t2":t2,"t3":t3,"t4":t4}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 8 困难与解决 ----------
with tabs[7]:
    part = "diff"; ans = st.session_state.answers.get(part, {})
    diffs = ["找不到相关文献","看不懂英文文献","不会提炼研究问题","不知道去哪里找数据",
             "不会使用数据分析软件","不会写学术论文","缺乏老师指导","不知道如何与导师沟通","其他"]
    order = st.multiselect("请将以下困难按对你困扰程度从高到低排序（第一个为最大）", diffs,
                           default=ans.get("order",[]))
    help_course = st.selectbox("学习这门课是否能有助解决这些困难？",
        ["非常有助","比较有助","一般","帮助不大","无帮助"],
        idx(["非常有助","比较有助","一般","帮助不大","无帮助"], ans.get("help_course","比较有助")))
    solve = st.text_area("最近一次遇到科研困难时，你是如何解决的？", ans.get("solve",""))
    if st.button("保存本部分", key="save_diff"):
        data = {"order":order,"help_course":help_course,"solve":solve}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")

# ---------- 9 总体自评 ----------
with tabs[8]:
    part = "self"; ans = st.session_state.answers.get(part, {})
    items = ["文献检索","AI工具辅助科研","提炼研究问题","数据获取","了解环境前沿","学术写作"]
    scores = {}
    st.markdown("**请对自己在以下方面的科研准备程度打分（1=完全没准备，5=准备充分）**")
    for it in items:
        scores[it] = st.slider(it, 1, 5, ans.get("scores",{}).get(it,3))
    wish = st.text_area("你希望这门课程最侧重教什么？", ans.get("wish",""))
    if st.button("保存本部分", key="save_self"):
        data = {"scores":scores,"wish":wish}
        save_part(sid,nick,part,data); st.session_state.answers[part]=data
        st.success("已保存")