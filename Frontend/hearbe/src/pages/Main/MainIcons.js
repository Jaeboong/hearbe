import React from 'react';
import { Link } from 'react-router-dom';
import { FaInfoCircle, FaQuestionCircle, FaDownload } from 'react-icons/fa';
// import './MainIcons.css'; // 이 파일은 더 이상 필요하지 않습니다.

const MainIcons = () => {
    // 음성 프로그램 다운로드 링크 (필요시 수정)
    const downloadLink = "/download/HearBeSetup.exe"; 

    return (
        <div className="flex justify-center items-end gap-[60px] mt-[50px] p-5">
            <Link to="/intro" className="flex cursor-pointer flex-col items-center text-[#4A4A4A] no-underline transition-all duration-300 hover:-translate-y-[5px] hover:text-[#007bff]">
                <FaInfoCircle size={50} />
                <span className="mt-3 text-base font-semibold">서비스 소개</span>
            </Link>
            <Link to="/guide" className="flex cursor-pointer flex-col items-center text-[#4A4A4A] no-underline transition-all duration-300 hover:-translate-y-[5px] hover:text-[#007bff]">
                <FaQuestionCircle size={50} />
                <span className="mt-3 text-base font-semibold">이용 가이드</span>
            </Link>
            <a href={downloadLink} className="relative flex cursor-pointer flex-col items-center text-[#4A4A4A] no-underline transition-all duration-300 hover:-translate-y-[5px] hover:text-[#007bff]" title="음성 프로그램 다운로드">
                <div className="absolute bottom-[calc(100%+15px)] left-1/2 -translate-x-1/2 whitespace-nowrap rounded-[25px] bg-[#007bff] py-[10px] px-4 text-[0.9rem] font-bold text-white shadow-[0_4px_12px_rgba(0,0,0,0.15)] after:absolute after:left-1/2 after:top-full after:-translate-x-1/2 after:border-8 after:border-solid after:border-x-transparent after:border-b-transparent after:border-t-[#007bff] after:content-['']">
                    음성 프로그램 다운로드
                </div>
                <FaDownload size={50} />
            </a>
        </div>
    );
};

export default MainIcons;