// 重载媒体库
function reloadLibrary() {
    if (confirm('确定要重载媒体库吗？这将刷新所有媒体文件和缩略图缓存。')) {
        fetch('/reload_library', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                alert('媒体库重载成功！');
                location.reload();
            } else {
                alert('重载失败，请检查控制台错误信息。');
            }
        }).catch(error => {
            alert('重载失败：' + error.message);
        });
    }
}

// 重启服务器
function restartServer() {
    if (confirm('确定要重启服务器吗？页面将自动刷新。')) {
        fetch('/restart_server', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            alert('服务器正在重启...');
            // 等待几秒后刷新页面
            setTimeout(() => {
                location.reload();
            }, 3000);
        }).catch(error => {
            // 重启时连接会断开，这是正常的
            alert('服务器正在重启...');
            setTimeout(() => {
                location.reload();
            }, 3000);
        });
    }
}
