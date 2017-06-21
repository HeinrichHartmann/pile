function assert {
    echo "$@"
    "$@" &&
      echo OK ||
        {
            echo NOK; exit 1;
        }
}

rm -r test
mkdir test
cd test

touch "2016-01-01   #TAG #TAG  #K:V name.ext"
touch "2016-01-01 #A #B #C name.ext"

pile normalize

assert [ -f "2016-01-01 #TAG #K:V name.ext" ]
assert [ -f "2016-01-01 #A #B #C name.ext" ]

pile extract \#A

assert [ -d "#A" ]
assert [ -f "#A/2016-01-01 #B #C name.ext" ]
assert [ ! -f "2016-01-01 #A #B #C name.ext" ]

pile fold \#A

assert [ -f "2016-01-01 #A #B #C name.ext" ]

