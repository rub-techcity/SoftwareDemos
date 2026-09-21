#pragma once
#include <string>
#include <vector>
#include <memory>
using namespace std;

// Component interface
class Component {
public:
	string name_Child_Composite;
	Component(string childNameArg);
	virtual void operationAutumn() = 0;
	virtual ~Component();
};

class Leaf : public Component {
public:
	Leaf(string leafName);
	void operationAutumn() override;
};

class Composite_Tree : public Component {
private:
	vector<unique_ptr<Component>> childrenCopmponents;
public:

	Composite_Tree(string treeNameArg);

	const int getAmountOfLeafs();

	void addChildComp(unique_ptr<Component> childCompArg);

	void removeChild(string leafName);

	void operationAutumn() override;

	void printLeafs();

	~Composite_Tree();
}; 
