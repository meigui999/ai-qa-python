<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">AI</div>
      <h2>欢迎回来</h2>
      <p class="auth-subtitle">登录 AI 智能问答系统</p>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">还没有账号？<a @click="$router.push('/register')">立即注册</a></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'

const router = useRouter(); const formRef = ref(); const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await login(form)
      localStorage.setItem('token', res.data?.token || res.token)
      localStorage.setItem('username', form.username)
      ElMessage.success('登录成功')
      router.push('/')
    } catch (e) {} finally { loading.value = false }
  })
}
</script>
