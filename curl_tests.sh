#!/bin/bash

echo 'create user david'
curl -XPOST localhost:5000/user/david
echo 'create user bruce'
curl -XPOST localhost:5000/user/bruce
echo 'create user lindsey'
curl -XPOST localhost:5000/user/lindsey

echo 'add zzsnzmn bitbucket to david'
curl -XPOST localhost:5000/user/david/bitbucket/zzsnzmn
echo 'add zzsnzmn bitbucket to david'
curl -XPOST localhost:5000/user/david/github/zzsnzmn

echo 'get david user profile'
curl -XGET localhost:5000/user/david

echo 'get bruce user profile'
curl -XGET localhost:5000/user/david

echo 'delete zzsnzmn bitbucket from david'
curl -XDELETE localhost:5000/user/david/bitbucket/zzsnzmn

echo 'delete zzsnzmn github from david'
curl -XDELETE localhost:5000/user/david/github/zzsnzmn

echo 'add zzsnzmn bitbucket to lindsey'
curl -XPOST localhost:5000/user/lindsey/bitbucket/zzsnzmn
echo 'add pygame bitbucket to lindsey'
curl -XPOST localhost:5000/user/lindsey/bitbucket/pygame
echo 'add kennethreitz github to lindsey'
curl -XPOST localhost:5000/user/lindsey/github/kennethreitz

echo 'get lindsey user profile'
curl -XGET localhost:5000/user/lindsey

echo 'delete zzsnzmn bitbucket from lindsey'
curl -XDELETE localhost:5000/user/lindsey/bitbucket/zzsnzmn

