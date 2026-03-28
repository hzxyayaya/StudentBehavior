import { createApp } from 'vue'

import App from './App.vue'
import { createAppPlugins } from './app/providers'
import './styles.css'

createApp(App).use(createAppPlugins()).mount('#app')
