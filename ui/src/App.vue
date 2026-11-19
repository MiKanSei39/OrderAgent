<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chat, getSession, newSession, request } from './api/client.js'

const tab = ref('chat')
const input = ref('')
const sending = ref(false)
const confirming = ref(false)
const messages = ref([])
const menu = ref([])
const orders = ref([])
const pending = ref(null)
const status = ref(null)
const suggestions = ref([])
const error = ref('')
const notice = ref('')
const category = ref('全部')
const menuSearch = ref('')
const vegetarian = ref(false)
const noSpicy = ref(false)
const chatBox = ref(null)
const draftLoading = ref(false)
let controller, faqTimer, faqSequence = 0
const form = reactive({ num_people: 2, num_children: 0, arrival_time: '', seat_preference: '不限', main_dish_preference: '不限', other_comments: '无' })
const starters = ['有什么特色菜？', '想吃清淡、不辣的菜', '我想预订明晚的座位', '营业时间是什么时候？']
const categories = computed(() => ['全部', ...new Set(menu.value.map(item => item.category))])
const visibleMenu = computed(() => menu.value.filter(item => (category.value === '全部' || item.category === category.value) && (!vegetarian.value || item.is_vegetarian) && (!noSpicy.value || item.spice_level === 0) && (item.dish_name + item.main_ingredients + item.flavor).includes(menuSearch.value.trim())))
const serviceLabel = computed(() => !status.value ? '连接服务中' : status.value.llm.configured ? '智能助手已就绪' : '基础服务可用 · 未配置模型')
const spice = level => ['不辣', '微辣', '中辣', '重辣'][level] || '待确认'
const dishIcon = id => ({ 1: '🥜', 2: '🥘', 3: '🥬', 4: '🐟', 5: '🥦' })[id] || '🍽️'
const renderAssistant = text => DOMPurify.sanitize(marked.parse(text, { breaks: true }), { ALLOWED_TAGS: ['p','br','strong','em','ul','ol','li','code','pre','blockquote','h1','h2','h3','table','thead','tbody','tr','th','td','hr'], ALLOWED_ATTR: [] })
const formatTime = value => (value || '').replace('T', ' ').replace('+08:00', '').slice(0, 16)
const scrollChat = async () => { await nextTick(); chatBox.value?.scrollTo({ top: chatBox.value.scrollHeight, behavior: 'smooth' }) }

async function refreshOrders() { orders.value = (await request('/reservation/list')).reservations }
async function refreshPending() { pending.value = (await request('/reservation/pending')).pending }
async function boot() {
  error.value = ''
  try {
    const [health, dishes, history, draft, reservations] = await Promise.all([request('/health'), request('/menu/list'), request('/chat/history'), request('/reservation/pending'), request('/reservation/list')])
    status.value = health; menu.value = dishes.menu_items; messages.value = history.messages; pending.value = draft.pending; orders.value = reservations.reservations
    scrollChat()
  } catch (e) { status.value = null; error.value = e.message + '。请确认后端已启动。' }
}

async function send(text = input.value) {
  text = text.trim()
  if (!text || sending.value || confirming.value) return
  tab.value = 'chat'; input.value = ''; suggestions.value = []; error.value = ''; notice.value = ''
  messages.value.push({ role: 'user', content: text })
  const answer = reactive({ role: 'assistant', content: '', tools: [] })
  messages.value.push(answer)
  sending.value = true; controller = new AbortController(); pending.value = null
  scrollChat()
  try {
    await chat(text, event => {
      if (event.type === 'token') answer.content += event.content
      else if (event.type === 'source') answer.source = event.content
      else if (event.type === 'tool') answer.tools.push(event.name)
      else if (event.type === 'reservation_pending') pending.value = event
      else if (event.type === 'reservation_created') { pending.value = null; refreshOrders().catch(e => { error.value = e.message }) }
      else if (event.type === 'reservation_cancelled') pending.value = null
      else if (event.type === 'error') { answer.content += '\n' + event.content; answer.failed = true }
      scrollChat()
    }, controller.signal)
  } catch (e) {
    if (e.name === 'AbortError') answer.content += '\n[已停止接收回复]'
    else { answer.content += '连接中断：' + e.message; answer.failed = true }
  } finally {
    sending.value = false; controller = null
    refreshPending().catch(() => {})
    scrollChat()
  }
}

async function resetSession() {
  if (sending.value || confirming.value) return
  newSession(); messages.value = []; pending.value = null; orders.value = []; error.value = ''; notice.value = '已开启新会话；旧会话记录与订单仍保存在原会话中。'
}

async function createDraft() {
  draftLoading.value = true; error.value = ''; notice.value = ''
  try {
    pending.value = await request('/reservation/draft', { method: 'POST', body: { ...form, arrival_time: form.arrival_time + ':00+08:00' } })
    notice.value = '草稿已生成，尚未下单。请核对确认单后再确认预订。'
  } catch (e) { error.value = e.message }
  finally { draftLoading.value = false }
}

async function confirmDraft() {
  if (!pending.value || confirming.value || sending.value) return
  confirming.value = true; error.value = ''; notice.value = ''
  try {
    const result = await request('/reservation/confirm', { method: 'POST', body: { token: pending.value.token } })
    pending.value = null; notice.value = '预订成功！订单编号 #' + result.reservation.id
    await refreshOrders()
  } catch (e) { error.value = e.message; await refreshPending().catch(() => {}) }
  finally { confirming.value = false }
}

async function cancelDraft() {
  if (sending.value || confirming.value) return
  try { await request('/reservation/pending', { method: 'DELETE' }); pending.value = null; notice.value = '已取消草稿，没有新增订单。' }
  catch (e) { error.value = e.message }
}

watch(input, value => {
  clearTimeout(faqTimer); const sequence = ++faqSequence; suggestions.value = []
  if (value.trim().length < 2 || sending.value) return
  faqTimer = setTimeout(async () => {
    try { const result = await request('/faq/suggest?query=' + encodeURIComponent(value) + '&limit=3'); if (sequence === faqSequence) suggestions.value = result.suggestions } catch {}
  }, 350)
})
watch(tab, value => { if (value === 'reservations') refreshOrders().catch(e => { error.value = e.message }); if (value === 'chat') scrollChat() })
onMounted(boot)
onBeforeUnmount(() => { controller?.abort(); clearTimeout(faqTimer) })
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#" @click.prevent="tab = 'chat'"><span class="brand-seal">六<br>合</span><span><strong>六合餐厅</strong><small>LIUHE · A TABLE FOR YOU</small></span></a>
      <nav aria-label="主导航"><button :class="{ active: tab === 'chat' }" @click="tab = 'chat'">智能助手</button><button :class="{ active: tab === 'menu' }" @click="tab = 'menu'">当季菜单 <span>{{ menu.length }}</span></button><button :class="{ active: tab === 'reservations' }" @click="tab = 'reservations'">我的预订 <span v-if="orders.length">{{ orders.length }}</span></button></nav>
      <div class="live-status" :class="{ offline: !status }"><i></i>{{ serviceLabel }}</div>
    </header>
    <main>
      <section class="page-intro"><div><p class="eyebrow">GOOD FOOD, GOOD COMPANY</p><h1>{{ tab === 'menu' ? '好食材，自有好滋味。' : tab === 'reservations' ? '为下一次相聚，留一席。' : '一席好味，从这里开始。' }}</h1><p class="intro-copy">{{ tab === 'menu' ? '从家常经典到清爽时蔬，找到今天想吃的那一道。' : tab === 'reservations' ? '填写心意，核对信息，再安心确认您的到店计划。' : '聊聊你的口味，把推荐和预订交给六合小助手。' }}</p></div><div class="intro-stamp">用心做菜<br><span>认真待客</span></div></section>
      <div v-if="error" class="banner error" role="alert">{{ error }} <button @click="error = ''" aria-label="关闭错误">×</button></div>
      <div v-if="notice" class="banner notice" role="status">{{ notice }} <button @click="notice = ''" aria-label="关闭提示">×</button></div>

      <div v-if="tab === 'chat'" class="chat-layout">
        <aside class="restaurant-sidebar">
          <div class="sidebar-art"><span class="art-leaf one"></span><span class="art-leaf two"></span><div class="bowl"><i></i><i></i><i></i></div><span class="art-label">吃好每一餐</span></div>
          <div class="sidebar-content"><p class="eyebrow">WELCOME TO LIUHE</p><h2>烟火日常，<br>也值得好好品尝。</h2><p class="muted">一口熟悉的味道，一段自在的时光。<br>很高兴，在六合遇见你。</p><hr><div class="info-row"><span>⌖</span><div><b>上海 · 人民广场</b><p>黄浦区人民广场六合大厦</p></div></div><div class="info-row"><span>◷</span><div><b>每天 10:00 开始营业</b><p>周日至周四至21:00<br>周五、周六至23:00</p></div></div><div class="info-row"><span>☎</span><div><b>联系我们</b><p><a href="tel:02112345678">021-12345678</a></p></div></div><button class="outline full" @click="tab = 'menu'">看看今日菜单 <span>↗</span></button></div>
        </aside>
        <section class="chat-panel" aria-label="智能点餐对话">
          <div class="panel-heading"><div class="assistant-name"><span class="avatar">合</span><div><b>六合小助手</b><small>懂你的口味，也记得你的偏好</small></div></div><button class="text-button" :disabled="sending || confirming" @click="resetSession">＋ 新会话</button></div>
          <div ref="chatBox" class="chat-scroll" role="log" aria-live="polite">
            <div v-if="!messages.length" class="chat-welcome"><span class="welcome-icon">✳</span><p class="eyebrow">YOUR PERSONAL DINING ASSISTANT</p><h2>今天，想吃点什么？</h2><p>告诉我你的口味、忌口，或想来的时间。<br>我会帮你挑好菜，也为你留好位置。</p><div class="starter-grid"><button v-for="(text, index) in starters" :key="text" @click="send(text)"><span>{{ ['✦', '❧', '▦', '◷'][index] }}</span>{{ text }}<i>↗</i></button></div></div>
            <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
              <span v-if="message.role === 'assistant'" class="mini-avatar">合</span>
              <div class="message-body">
                <span v-if="message.source" class="message-source">{{ message.source }}</span>
                <div v-if="message.role === 'assistant'" class="message-text markdown" :class="{ failed: message.failed }" v-html="renderAssistant(message.content || (sending ? '正在为你查看…' : '暂无回复'))"></div>
                <div v-else class="message-text">{{ message.content }}</div>
                <small v-if="message.tools?.length" class="tool-trace">已查询 · {{ [...new Set(message.tools)].map(name => ({ search_menu: '餐厅菜单', user_flavor_search: '口味推荐', make_reservation: '预订草稿', current_restaurant_time: '上海时间' })[name] || '辅助工具').join(' / ') }}</small>
              </div>
            </div>
          </div>
          <div v-if="pending" class="inline-draft"><div><b>预订信息已备好，等待你的确认</b><p>{{ formatTime(pending.reservation.arrival_time) }} · {{ pending.reservation.num_people }}人（含{{ pending.reservation.num_children }}位儿童） · {{ pending.reservation.seat_preference }}</p><p>主菜：{{ pending.reservation.main_dish_preference }} · 备注：{{ pending.reservation.other_comments }}</p></div><div class="draft-actions"><button class="text-button" :disabled="sending || confirming" @click="cancelDraft">取消草稿</button><button class="primary" :disabled="sending || confirming" @click="confirmDraft">{{ confirming ? '确认中…' : '确认预订' }}</button></div></div>
          <div class="composer"><div v-if="suggestions.length" class="faq-suggestions"><small>你可能想问</small><button v-for="item in suggestions" :key="item.id" @click="send(item.question)">{{ item.question }} ↗</button></div><div class="input-wrap"><textarea v-model="input" rows="2" maxlength="4000" aria-label="输入点餐问题" placeholder="例如：两个人想吃清淡一点的，有什么推荐？" @keydown.enter.exact.prevent="!$event.isComposing && send()"></textarea><button v-if="sending" class="send stop" @click="controller?.abort()" aria-label="停止接收回复">■</button><button v-else class="send" :disabled="!input.trim() || confirming" @click="send()" aria-label="发送消息">↑</button></div><div class="composer-foot"><span>Enter发送 · Shift+Enter换行</span><span>过敏与特殊需求，请同时告知大堂</span></div></div>
        </section>
      </div>

      <section v-else-if="tab === 'menu'" class="menu-section">
        <div class="menu-toolbar"><div class="category-tabs"><button v-for="name in categories" :key="name" :class="{ selected: category === name }" @click="category = name">{{ name }}</button></div><input v-model="menuSearch" class="search" placeholder="搜索菜名、食材或口味" aria-label="搜索菜单"></div><div class="menu-filters"><span>按喜好筛选</span><label><input type="checkbox" v-model="vegetarian"> 只看素食</label><label><input type="checkbox" v-model="noSpicy"> 只看不辣</label><small>共 {{ visibleMenu.length }} 道菜品</small></div>
        <div class="menu-grid"><article v-for="item in visibleMenu" :key="item.id" class="dish-card"><div class="dish-art" :class="'dish-' + item.id"><span>{{ dishIcon(item.id) }}</span><b v-if="item.is_featured" class="featured-label">六合招牌</b><small>菜品示意 · 非实拍</small></div><div class="dish-content"><div class="dish-title"><h2>{{ item.dish_name }}</h2><strong><small>¥</small>{{ item.price.toFixed(2) }}</strong></div><p>{{ item.description }}</p><div class="dish-tags"><span>{{ item.category }}</span><span :class="{ spicy: item.spice_level > 0 }">{{ spice(item.spice_level) }}</span><span v-if="item.is_vegetarian" class="vegetarian">素食</span></div><div class="ingredients"><b>主要食材</b>{{ item.main_ingredients }}</div><div class="allergens"><b>过敏原提示</b>{{ item.allergens || '未提供过敏原记录，请与大堂确认' }}</div><button class="dish-ask" @click="send('请介绍一下' + item.dish_name + '，适合什么口味的人？')">问问小助手 <span>↗</span></button></div></article></div><div v-if="!visibleMenu.length" class="empty-state">暂时没有符合条件的菜品，试试调整筛选条件。</div>
      </section>

      <section v-else class="reservation-layout">
        <div class="reservation-form card"><div class="section-title"><p class="eyebrow">MAKE A RESERVATION</p><h2>提前留座，从容相聚</h2><p>先填写、再核对，确认后才会生成订单。</p></div><form @submit.prevent="createDraft"><div class="form-row"><label>到店总人数（含儿童）<input type="number" v-model.number="form.num_people" min="1" max="20" required></label><label>其中0—5岁儿童<input type="number" v-model.number="form.num_children" min="0" :max="form.num_people" required></label></div><label>到店时间 <small>上海时间</small><input type="datetime-local" v-model="form.arrival_time" required></label><label>座位偏好<select v-model="form.seat_preference"><option>不限</option><option>靠窗</option><option>安静区域</option><option>方便儿童就座</option></select></label><label>主菜或口味偏好<input v-model="form.main_dish_preference" maxlength="100" required placeholder="如：清淡、不辣；无要求填不限"></label><label>其他备注<textarea v-model="form.other_comments" rows="3" maxlength="1000" required placeholder="请说明过敏、忌口等；无要求填无"></textarea></label><p class="form-note">座位和主菜偏好为预约需求，不代表已锁定具体桌位或菜品库存。</p><button class="primary full" :disabled="draftLoading || sending || confirming">{{ draftLoading ? '生成中…' : '生成预订确认单 →' }}</button></form></div>
        <div class="reservation-right"><div v-if="pending" class="confirmation-card card"><p class="eyebrow">ONE MORE STEP</p><h2>请核对你的预订</h2><span class="pending-badge">待二次确认 · 尚未下单</span><dl><dt>到店时间</dt><dd>{{ formatTime(pending.reservation.arrival_time) }}</dd><dt>用餐人数</dt><dd>{{ pending.reservation.num_people }}人（含{{ pending.reservation.num_children }}位儿童）</dd><dt>座位偏好</dt><dd>{{ pending.reservation.seat_preference }}</dd><dt>主菜偏好</dt><dd>{{ pending.reservation.main_dish_preference }}</dd><dt>其他备注</dt><dd>{{ pending.reservation.other_comments }}</dd></dl><div class="draft-actions"><button class="outline" :disabled="confirming || sending" @click="cancelDraft">取消草稿</button><button class="primary" :disabled="confirming || sending" @click="confirmDraft">{{ confirming ? '正在确认…' : '信息无误，确认预订' }}</button></div></div><div class="orders-card card"><div class="orders-heading"><div><p class="eyebrow">YOUR RESERVATIONS</p><h2>我的预订单 <small>{{ orders.length }}</small></h2></div><button class="text-button" @click="refreshOrders().catch(e => error = e.message)">刷新 ↻</button></div><p class="muted">仅展示当前会话的预订，避免泄露其他客人信息。</p><div v-if="!orders.length" class="empty-state"><span>▦</span><h3>期待与你相聚</h3><p>确认预订后，订单会出现在这里。</p></div><article v-for="order in orders" :key="order.id" class="order-item"><div><b>预订 #{{ order.id }}</b><span class="order-status">已确认</span></div><h3>{{ formatTime(order.arrival_time) }}</h3><p>{{ order.num_people }}人 · 含{{ order.num_children }}位儿童 · {{ order.seat_preference }}</p><p>主菜：{{ order.main_dish_preference }}</p><p>备注：{{ order.other_comments }}</p></article></div></div>
      </section>
      <footer><span>六合餐厅 · 把日常吃成喜欢的样子</span><span v-if="status">{{ status.database === 'mysql' ? 'MySQL' : 'SQLite演示库' }} · {{ status.faq === 'redis' ? 'Redis FAQ' : '本地FAQ' }} · {{ status.retrieval === 'milvus' ? 'Milvus语义检索' : '本地词法检索' }}</span></footer>
    </main>
  </div>
</template>
