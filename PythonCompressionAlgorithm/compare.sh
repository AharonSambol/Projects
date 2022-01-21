BASEDIR=/Aharon/git/ajs-code/python/PythonCompressionAlgorithm
PYTHON=/cygdrive/D/Aharon/git/ajs-code/python/venv310/Scripts/python.exe
# on linux / chromebook:
# HOME=/home/aharonsambol
# BASEDIR = $HOME/code/advent/
CYGBINS=/cygdrive/D/cygwin64/bin

echo compressing python files in $1
fname=`basename $1`
cp -R $1 /tmp
echo done copying...
$PYTHON $BASEDIR/Compress.py /tmp/$fname False x x
echo comparing results...
$CYGBINS/tar cf /tmp/pre-compression.tar `$CYGBINS/find $1 -name '*.py'`
$CYGBINS/tar cf /tmp/post-compression.tar `$CYGBINS/find /tmp/$fname -name '*.py'`
gzip /tmp/pre-compression.tar
gzip /tmp/post-compression.tar
##ls -l /tmp/*-compress*.gz
size1=`du /tmp/pre-compression.tar.gz | cut -f 1`
echo pre-compression size is $size1
size2=`du /tmp/post-compression.tar.gz | cut -f 1`
echo post-compression size is $size2
echo detailed size:
du /tmp/pre-compression.tar.gz | cut -f 1
du /tmp/post-compression.tar.gz | cut -f 1
echo ratio is $(($size2 *100 / $size1))
rm -rf /tmp/$fname
rm /tmp/pre-compression.tar.gz
rm /tmp/post-compression.tar.gz
