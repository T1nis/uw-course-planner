import React, { useState } from 'react';
import { CheckCircle, Circle, Calendar, TrendingUp, BookOpen, Award, AlertCircle, Target, Clock, Users } from 'lucide-react';

const ProgressPage = () => {
  const [selectedSemester, setSelectedSemester] = useState('current');
  
  // Mock data for demonstration
  const studentData = {
    name: "Alex Johnson",
    major: "Computer Science",
    gpa: 3.42,
    creditsCompleted: 78,
    totalCreditsRequired: 120,
    expectedGraduation: "Spring 2025",
    currentSemester: "Fall 2024"
  };

  const graduationRequirements = [
    {
      category: "Core Requirements",
      totalCredits: 45,
      completedCredits: 42,
      courses: [
        { name: "Calculus I", credits: 4, completed: true, grade: "A-" },
        { name: "Calculus II", credits: 4, completed: true, grade: "B+" },
        { name: "Physics I", credits: 4, completed: true, grade: "B" },
        { name: "English Composition", credits: 3, completed: true, grade: "A" },
        { name: "Data Structures", credits: 4, completed: true, grade: "A" },
        { name: "Algorithms", credits: 4, completed: true, grade: "B+" },
        { name: "Computer Architecture", credits: 4, completed: true, grade: "B" },
        { name: "Operating Systems", credits: 4, completed: true, grade: "B+" },
        { name: "Database Systems", credits: 4, completed: true, grade: "A-" },
        { name: "Software Engineering", credits: 4, completed: true, grade: "A" },
        { name: "Ethics in Computing", credits: 3, completed: true, grade: "A" },
        { name: "Statistics", credits: 3, completed: false, grade: null }
      ]
    },
    {
      category: "Major Electives",
      totalCredits: 24,
      completedCredits: 16,
      courses: [
        { name: "Machine Learning", credits: 4, completed: true, grade: "A" },
        { name: "Web Development", credits: 4, completed: true, grade: "A-" },
        { name: "Mobile App Development", credits: 4, completed: true, grade: "B+" },
        { name: "Computer Graphics", credits: 4, completed: true, grade: "B" },
        { name: "Cybersecurity", credits: 4, completed: false, grade: null },
        { name: "Artificial Intelligence", credits: 4, completed: false, grade: null }
      ]
    },
    {
      category: "General Education",
      totalCredits: 36,
      completedCredits: 20,
      courses: [
        { name: "World History", : 3, completed: true, grade: "B+" },
        { name: "Psychology 101", crecreditsdits: 3, completed: true, grade: "A-" },
        { name: "Literature", credits: 3, completed: true, grade: "B" },
        { name: "Philosophy", credits: 3, completed: true, grade: "A" },
        { name: "Art History", credits: 3, completed: true, grade: "B+" },
        { name: "Foreign Language I", credits: 3, completed: true, grade: "B" },
        { name: "Biology", credits: 2, completed: true, grade: "B+" },
        { name: "Chemistry", credits: 0, completed: false, grade: null },
        { name: "Foreign Language II", credits: 3, completed: false, grade: null },
        { name: "Social Science Elective", credits: 3, completed: false, grade: null },
        { name: "Humanities Elective", credits: 3, completed: false, grade: null },
        { name: "Science Elective", credits: 3, completed: false, grade: null },
        { name: "Free Elective", credits: 3, completed: false, grade: null }
      ]
    },
    {
      category: "Capstone Project",
      totalCredits: 6,
      completedCredits: 0,
      courses: [
        { name: "Senior Design I", credits: 3, completed: false, grade: null },
        { name: "Senior Design II", credits: 3, completed: false, grade: null }
      ]
    }
  ];

  const semesterProgress = [
    { semester: "Fall 2022", gpa: 3.2, credits: 15, cumulativeGPA: 3.2 },
    { semester: "Spring 2023", gpa: 3.6, credits: 16, cumulativeGPA: 3.4 },
    { semester: "Fall 2023", gpa: 3.4, credits: 15, cumulativeGPA: 3.4 },
    { semester: "Spring 2024", gpa: 3.5, credits: 16, cumulativeGPA: 3.42 },
    { semester: "Fall 2024", gpa: 0, credits: 16, cumulativeGPA: 3.42, current: true }
  ];

  const upcomingDeadlines = [
    { task: "Course Registration", date: "Nov 15, 2024", type: "registration" },
    { task: "Midterm Exams", date: "Oct 28, 2024", type: "exam" },
    { task: "Financial Aid Application", date: "Dec 1, 2024", type: "financial" },
    { task: "Graduation Application", date: "Feb 1, 2025", type: "graduation" }
  ];

  const getProgressColor = (completed, total) => {
    const percentage = (completed / total) * 100;
    if (percentage >= 100) return 'bg-green-400';
    if (percentage >= 75) return 'bg-blue-400';
    if (percentage >= 50) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  const getGradeColor = (grade) => {
    if (!grade) return 'text-gray-400';
    if (grade.startsWith('A')) return 'text-green-400';
    if (grade.startsWith('B')) return 'text-blue-400';
    if (grade.startsWith('C')) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#171923] via-[#22223c] to-[#29304d] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white/10 border border-white/20 rounded-xl shadow-xl backdrop-blur-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Academic Progress</h1>
              <p className="text-gray-300 mt-1">{studentData.name} • {studentData.major}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-400">{studentData.gpa}</div>
              <div className="text-sm text-gray-300">Cumulative GPA</div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white/10 border border-white/20 rounded-lg p-6 shadow-xl backdrop-blur-lg">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-blue-400" />
              <div className="ml-3">
                <div className="text-2xl font-bold text-white">{studentData.creditsCompleted}</div>
                <div className="text-sm text-gray-300">Credits Completed</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 border border-white/20 rounded-lg p-6 shadow-xl backdrop-blur-lg">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-green-400" />
              <div className="ml-3">
                <div className="text-2xl font-bold text-white">{Math.round((studentData.creditsCompleted / studentData.totalCreditsRequired) * 100)}%</div>
                <div className="text-sm text-gray-300">Degree Progress</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 border border-white/20 rounded-lg p-6 shadow-xl backdrop-blur-lg">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-purple-400" />
              <div className="ml-3">
                <div className="text-2xl font-bold text-white">{studentData.expectedGraduation}</div>
                <div className="text-sm text-gray-300">Expected Graduation</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white/10 border border-white/20 rounded-lg p-6 shadow-xl backdrop-blur-lg">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-orange-400" />
              <div className="ml-3">
                <div className="text-2xl font-bold text-white">{studentData.totalCreditsRequired - studentData.creditsCompleted}</div>
                <div className="text-sm text-gray-300">Credits Remaining</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Graduation Requirements */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 border border-white/20 rounded-xl shadow-xl backdrop-blur-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <Award className="h-5 w-5 text-blue-400 mr-2" />
                Graduation Requirements
              </h2>
              
              <div className="space-y-6">
                {graduationRequirements.map((requirement, index) => (
                  <div key={index} className="border border-white/20 rounded-lg p-4 bg-white/5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-white">{requirement.category}</h3>
                      <span className="text-sm text-gray-300">
                        {requirement.completedCredits}/{requirement.totalCredits} credits
                      </span>
                    </div>
                    
                    <div className="w-full bg-white/10 rounded-full h-2 mb-3">
                      <div 
                        className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(requirement.completedCredits, requirement.totalCredits)}`}
                        style={{ width: `${Math.min((requirement.completedCredits / requirement.totalCredits) * 100, 100)}%` }}
                      ></div>
                    </div>
                    
                    <div className="space-y-2">
                      {requirement.courses.map((course, courseIndex) => (
                        <div key={courseIndex} className="flex items-center justify-between text-sm">
                          <div className="flex items-center">
                            {course.completed ? (
                              <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                            ) : (
                              <Circle className="h-4 w-4 text-gray-400 mr-2" />
                            )}
                            <span className={course.completed ? 'text-gray-200' : 'text-gray-400'}>
                              {course.name}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-300">{course.credits} cr</span>
                            {course.grade && (
                              <span className={`font-medium ${getGradeColor(course.grade)}`}>
                                {course.grade}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upcoming Deadlines */}
            <div className="bg-white/10 border border-white/20 rounded-xl shadow-xl backdrop-blur-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <AlertCircle className="h-5 w-5 text-orange-400 mr-2" />
                Upcoming Deadlines
              </h2>
              
              <div className="space-y-3">
                {upcomingDeadlines.map((deadline, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-lg">
                    <div>
                      <div className="font-medium text-white text-sm">{deadline.task}</div>
                      <div className="text-xs text-gray-300">{deadline.date}</div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      deadline.type === 'exam' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                      deadline.type === 'registration' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                      deadline.type === 'financial' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                      'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                    }`}>
                      {deadline.type}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Semester Performance */}
            <div className="bg-white/10 border border-white/20 rounded-xl shadow-xl backdrop-blur-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 text-green-400 mr-2" />
                Semester Performance
              </h2>
              
              <div className="space-y-3">
                {semesterProgress.map((semester, index) => (
                  <div key={index} className={`p-3 rounded-lg ${semester.current ? 'bg-blue-500/20 border border-blue-500/30' : 'bg-white/5 border border-white/10'}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-white text-sm">
                          {semester.semester}
                          {semester.current && <span className="ml-2 text-xs bg-blue-500/80 text-white px-2 py-1 rounded">Current</span>}
                        </div>
                        <div className="text-xs text-gray-300">{semester.credits} credits</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-white">{semester.current ? 'In Progress' : semester.gpa}</div>
                        <div className="text-xs text-gray-300">GPA: {semester.cumulativeGPA}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white/10 border border-white/20 rounded-xl shadow-xl backdrop-blur-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
              
              <div className="space-y-2">
                <button className="w-full text-left p-3 rounded-lg bg-blue-500/20 border border-blue-500/30 hover:bg-blue-500/30 transition-colors">
                  <div className="font-medium text-blue-300">Plan Next Semester</div>
                  <div className="text-sm text-blue-200">Add courses to your schedule</div>
                </button>
                
                <button className="w-full text-left p-3 rounded-lg bg-green-500/20 border border-green-500/30 hover:bg-green-500/30 transition-colors">
                  <div className="font-medium text-green-300">Academic Advisor</div>
                  <div className="text-sm text-green-200">Schedule a meeting</div>
                </button>
                
                <button className="w-full text-left p-3 rounded-lg bg-purple-500/20 border border-purple-500/30 hover:bg-purple-500/30 transition-colors">
                  <div className="font-medium text-purple-300">Degree Audit</div>
                  <div className="text-sm text-purple-200">Generate full report</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressPage;