from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from .models import Student, Work
import xlwt
import os
from io import BytesIO
from django.contrib.auth.hashers import make_password, check_password
from itsdangerous import TimedJSONWebSignatureSerializer as Ts
from django.conf import settings


#/worktime/regist/
def regist(request):
    '''显示注册页面'''
    if request.method == 'GET':
        return render(request, 'regist.html')
    '''进行注册处理'''
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        try:
            user = User.objects.get(username = student_id)
        except User.DoesNotExist:
            user = None
        if not all([student_id, password, password2]):
            return render(request, 'regist.html', {'errmsg': '数据不完整'})
        elif user:
            return render(request, 'regist.html', {'errmsg': '用户名已注册'})
        elif password !=password2:
            return render(request, 'regist.html', {'errmsg': '两次输入密码不一致'})
        else:
            user = User.objects.create_user(username=student_id, password=password)
            # # user.is_active = 0
            # # user.save()
            # #加密
            # ts = Ts(settings.SECRET_KEY,600)
            # info= {'confirm':user.id}
            # token = ts.dump(info)
            # return HttpResponseRedirect('/worktime/login')
            return redirect(reverse('worktime:login'))


#/worktime/login/
def login(request):
    '''显示提交页面'''
    if request.method == 'GET':
        return render(request, 'login.html')
    '''进行提交处理'''
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        # 验证用户名和密码，通过的话，返回User对象
        try:
            user2 = User.objects.get(username = student_id)
        except User.DoesNotExist:
            user2 = None
        if not user2:
            return render(request, 'login.html', {'errmsg': '用户名不存在'})
        else:
            if student_id =='superuser':
                return redirect(reverse('worktime:superuser'))
            else:
                user = auth.authenticate(username=student_id, password=password)
                if user:
                    auth.login(request, user)
                    return redirect(reverse('worktime:index', args=(student_id,)))
                else:
                    return render(request, 'login.html', {'errmsg': '密码错误'})


#/worktime/index
def index(request,student_id):
    try:
        Student.objects.get(Student_id = student_id)
    except Student.DoesNotExist:
        '''用户未进行信息绑定'''
        if request.method == 'GET':
            '''显示信息页面'''
            return render(request, 'index.html')
        if request.method =='POST':
            '''进行信息绑定'''
            student_name = request.POST.get('student_name')
            student_department= request.POST.get('student_department')
            student_position= request.POST.get('student_position')
            Student.objects.create(Student_id = student_id, Student_name = student_name, Student_department = student_department, Student_position = student_position)
        '''已绑定'''
    return redirect(reverse('worktime:submit',args=(student_id,)))


#/worktime/submit
def submit(request, student_id):
    if request.method == 'GET':
        return render(request, 'submit.html')
    if request.method == 'POST':
        which_week = request.POST.get('which_week')
        work_times = request.POST.get('work_times')
        work_details = request.POST.get('work_details')
        if not all([which_week, work_times, work_details]):
            return render(request, 'submit.html', {'errmsg': '数据不完整，请重新输入'})
        else:
            try:
                Work.objects.create(work_id=student_id, which_week=which_week, work_times=work_times,
                                               work_details=work_details)
                return redirect(reverse('worktime:logout', args=(student_id,)))
            except:
                return render(request,'submit.html',{'errmsg':'该周工作量已提交'})


#/worktime/logout/
def logout(request,student_id,):
    if request.method == 'GET':
        auth.logout(request)
        all_works = Work.objects.all().filter(work = student_id)
        name = Student.objects.get(Student_id = student_id)
        return render(request,'logout.html',{'all_works' : all_works,'name':name})


#/worktime/superuser/
def superuser(request):
    if request.method == 'GET':
        return render(request, 'superuser.html')
    if request.method == 'POST':
        week = request.POST.get('which_week')
        department = request.POST.get('student_department')
        if not all([department, week,]):
            return render(request, 'superuser.html', {'errmsg': '数据不完整，请选择部门和工作周'})
        else:
            stu = Student.objects.filter(work__which_week = week,Student_department = department)
            department_works = Work.objects.filter(work__Student_department =department,which_week = week)
            return render(request,'superuser.html',{'department_works':department_works,'students':stu})


#superuser/export_excel/
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="students_work.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('order-sheet')
    # Sheet header, first row
    style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)
    sheet.write(0, 0, '部门', style_heading)
    sheet.write(0, 1, '第几周', style_heading)
    sheet.write(0, 2, '工作时长', style_heading)
    sheet.write(0, 3, '工作详情', style_heading)
    sheet.write(0, 4, '学号', style_heading)
    sheet.write(0, 5, '姓名', style_heading)
    data_row = 1

    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(
        'select student_department 部门,student_id 学号,student_name 姓名,which_week 第几周,work_times 工作时长,work_details 工作详情 from student_test,worktime_test where student_id = work_id ORDER BY  student_department, which_week')
    row = cursor.fetchall()
    data_row = 1
    for i in row:
        if  i[0] == 0:
            sheet.write(data_row, 0, '技术开发部')
        elif i[0] == 1:
            sheet.write(data_row, 0, '秘书部')
        elif i[0] == 2:
            sheet.write(data_row, 0, '编辑部')
        elif i[0] == 3:
            sheet.write(data_row, 0, '管理部')
        elif i[0] == 4:
            sheet.write(data_row, 0, '部门5')
        elif i[0] == 5:
            sheet.write(data_row, 0, '部门6')
        elif i[0] == 6:
            sheet.write(data_row, 0, '部门7')
        else:
            sheet.write(data_row, 0, '部门8')
        sheet.write(data_row, 1, i[3])
        sheet.write(data_row, 2, i[4])
        sheet.write(data_row, 3, i[5])
        sheet.write(data_row, 4, i[1])
        sheet.write(data_row, 5, i[2])
        data_row = data_row + 1
    #保存到本地
    # exist_file = os.path.exists("students_work.xls")
    # if exist_file:
    #     os.remove(r"students_work.xls")
    # wb.save("students_work.xls")

    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response