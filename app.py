import os
import tempfile
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from markitdown import MarkItDown
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 配置日志
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/2markdown.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('2markdown启动')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件被上传
    if 'file' not in request.files:
        app.logger.warning('无文件部分')
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        app.logger.warning('未选择文件')
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        app.logger.warning(f'不支持的文件类型: {file.filename}')
        return jsonify({'error': '不支持的文件类型'}), 400
    
    try:
        app.logger.info(f'处理文件: {file.filename}')
        
        # 保存上传的文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        app.logger.info(f'文件保存到临时位置: {temp_path}')
        
        # 初始化MarkItDown
        md = MarkItDown()
        
        # 转换文件
        app.logger.info(f'开始转换文件: {file.filename}')
        result = md.convert(temp_path)
        
        # 将转换后的内容保存到内存中
        md_content = result.text_content
        app.logger.info(f'文件转换完成: {file.filename}')
        
        # 删除临时文件
        os.unlink(temp_path)
        app.logger.info(f'临时文件已删除: {temp_path}')
        
        # 准备输出文件
        output_filename = secure_filename(os.path.splitext(file.filename)[0] + '.md')
        
        # 创建内存文件对象
        md_file = io.BytesIO(md_content.encode('utf-8'))
        
        app.logger.info(f'发送转换后的文件: {output_filename}')
        
        # 返回下载链接
        return send_file(
            md_file,
            as_attachment=True,
            download_name=output_filename,
            mimetype='text/markdown'
        )
    
    except Exception as e:
        # 确保临时文件被删除
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
                app.logger.info(f'错误处理中删除临时文件: {temp_path}')
            except:
                pass
        
        app.logger.error(f'处理文件时出错: {str(e)}', exc_info=True)
        return jsonify({'error': f'转换过程中出错: {str(e)}'}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('服务器错误', exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 