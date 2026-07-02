import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

BACKUP_DIR = os.getenv('BACKUP_DIR', './backups')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))

def init_backup_scheduler(app):
    """初始化备份调度器"""
    from apscheduler.schedulers.background import BackgroundScheduler
    import atexit
    
    scheduler = BackgroundScheduler()
    
    # 每天晚上 2 点执行自动备份
    scheduler.add_job(
        func=create_backup,
        trigger="cron",
        hour=2,
        minute=0,
        id='auto_backup',
        name='自动备份',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=cleanup_old_backups,
        trigger="cron",
        hour=3,
        minute=0,
        id='cleanup_backups',
        name='清理旧备份',
        replace_existing=True
    )
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

def create_backup(backup_type='full'):
    """创建备份"""
    # 确保备份目录存在
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'hvac_crm_backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # 复制数据库文件
        source_db = 'database.db'
        if os.path.exists(source_db):
            shutil.copy2(source_db, backup_path)
            
            # 获取文件大小
            file_size = os.path.getsize(backup_path)
            
            return {
                'filename': backup_filename,
                'file_path': backup_path,
                'file_size': file_size,
                'timestamp': timestamp
            }
        else:
            raise FileNotFoundError(f'源数据库 {source_db} 不存在')
    except Exception as e:
        raise Exception(f'备份失败: {str(e)}')

def restore_backup(backup_file_path):
    """恢复备份"""
    if not os.path.exists(backup_file_path):
        raise FileNotFoundError(f'备份文件 {backup_file_path} 不存在')
    
    try:
        target_db = 'database.db'
        
        # 创建备份文件的备份
        if os.path.exists(target_db):
            backup_of_current = f'{target_db}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy2(target_db, backup_of_current)
        
        # 恢复
        shutil.copy2(backup_file_path, target_db)
        
    except Exception as e:
        raise Exception(f'恢复失败: {str(e)}')

def cleanup_old_backups():
    """清理旧备份"""
    cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
    
    if not os.path.exists(BACKUP_DIR):
        return
    
    for file in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, file)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if file_mtime < cutoff_date:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'删除文件 {file} 失败: {str(e)}')
