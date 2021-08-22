import Vue from 'vue'
import App from './App'
import store from './store'
import './css/app.css'
import '../static/weui.css'
import 'animate.css'

Vue.config.productionTip = false
App.mpType = 'app'
Vue.prototype.$store = store

const app = new Vue(App)
app.$mount()

export default {
    // 这个字段走 app.json
    config: {
        // 页面前带有 ^ 符号的，会被编译成首页，其他页面可以选填，我们会自动把 webpack entry 里面的入口页面加进去
        pages: ['pages/logs/main', '^pages/index/main',
            'pages/product-list/main', 'pages/cart/main', 'pages/account/main', 'pages/product-detail/main'],
        window: {
            backgroundTextStyle: 'light',
            navigationBarBackgroundColor: '#fff',
            navigationBarTitleText: 'WeChat',
            navigationBarTextStyle: 'black'
        },
        tabBar: {
            color: '#999999',
            selectedColor: '#1AAD16',
            backgroundColor: '#ffffff',
            borderStyle: 'white',
            /* eslint-disable */
            list: [{
                pagePath: 'pages/index/main',
                text: 'Home',
                iconPath: 'static/images/navhome.png',
                selectedIconPath: 'static/images/navhome_sel.png'
            },
                {
                    pagePath: 'pages/product-list/main',
                    text: 'Product',
                    iconPath: 'static/images/navtype.png',
                    selectedIconPath: 'static/images/navtype_sel.png'
                },
                {
                    pagePath: 'pages/cart/main',
                    text: 'Cart',
                    iconPath: 'static/images/navcart.png',
                    selectedIconPath: 'static/images/navcart_sel.png'
                },
                {
                    pagePath: 'pages/account/main',
                    text: 'Me',
                    iconPath: 'static/images/navme.png',
                    selectedIconPath: 'static/images/navme_sel.png'
                }
            ]
            /* eslint-enable */
        }
    }
}
