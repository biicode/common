program Hello
      integer::narg,cptArg
      character(100)::name
    
      narg=command_argument_count()
    
      if(narg>0)then
         do cptArg=1,narg
            call get_command_argument(cptArg,name)
            write(*, "(A)") trim(name)
         end do
      end if
      INCLUDE 'hello.f90'      
end program Hello
