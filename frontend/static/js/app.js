new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        isLoggedIn: false,
        isLogin: true,
        user: null,
        authForm: {
            username: '',
            email: '',
            password: ''
        },
        profile: {
            age: null,
            gender: '',
            skin_type: '',
            concerns: ''
        },
        showProfile: false,
        isCameraActive: false,
        showResult: false,
        showHistory: false,
        result: {
            image: '',
            score: 0,
            moisture: 0,
            oil: 0,
            sensitivity: 0,
            recommendations: ''
        },
        history: [],
        stream: null
    },
    created() {
        // 检查本地存储中的认证状态
        const token = localStorage.getItem('token');
        if (token) {
            this.isLoggedIn = true;
            this.user = JSON.parse(localStorage.getItem('user'));
            this.loadProfile();
            this.loadHistory();
        }
    },
    methods: {
        async handleAuth() {
            try {
                const url = this.isLogin ? '/api/login' : '/api/register';
                const response = await axios.post(url, this.authForm);
                
                if (this.isLogin) {
                    const { access_token, user } = response.data;
                    localStorage.setItem('token', access_token);
                    localStorage.setItem('user', JSON.stringify(user));
                    this.isLoggedIn = true;
                    this.user = user;
                    this.loadProfile();
                    this.loadHistory();
                } else {
                    this.isLogin = true;
                    this.authForm = {
                        username: '',
                        email: '',
                        password: ''
                    };
                }
            } catch (error) {
                console.error('认证失败:', error);
                alert(error.response?.data?.error || '认证失败，请重试');
            }
        },
        logout() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            this.isLoggedIn = false;
            this.user = null;
            this.stopCamera();
        },
        async loadProfile() {
            try {
                const response = await axios.get('/api/profile', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                });
                this.profile = response.data;
            } catch (error) {
                console.error('加载个人资料失败:', error);
            }
        },
        async updateProfile() {
            try {
                await axios.put('/api/profile', this.profile, {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                });
                this.showProfile = false;
                alert('个人资料更新成功');
            } catch (error) {
                console.error('更新个人资料失败:', error);
                alert('更新失败，请重试');
            }
        },
        async startCamera() {
            try {
                this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
                this.$refs.video.srcObject = this.stream;
                this.isCameraActive = true;
            } catch (error) {
                console.error('启动相机失败:', error);
                alert('无法访问相机，请检查权限设置');
            }
        },
        stopCamera() {
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.$refs.video.srcObject = null;
                this.isCameraActive = false;
            }
        },
        async captureImage() {
            const video = this.$refs.video;
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            try {
                const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
                const formData = new FormData();
                formData.append('image', blob);
                
                const response = await axios.post('/api/analyze', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                
                this.result = {
                    ...response.data,
                    image: URL.createObjectURL(blob)
                };
                this.showResult = true;
                this.stopCamera();
                this.loadHistory();
            } catch (error) {
                console.error('分析失败:', error);
                alert('分析失败，请重试');
            }
        },
        async loadHistory() {
            try {
                const response = await axios.get('/api/history', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                });
                this.history = response.data;
            } catch (error) {
                console.error('加载历史记录失败:', error);
            }
        },
        formatDate(dateString) {
            return new Date(dateString).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
});