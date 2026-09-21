#include <iostream>
#include "CompositePattern.h"
using namespace std;

// Component interface
Component::Component(string childNameArg) : name_Child_Composite(childNameArg) {};
Component::~Component() {
		cout << "    Removing the "<< '"' << name_Child_Composite << '"' <<" .\n";
}

Leaf::Leaf(string leafName) : Component(leafName) {};

void Leaf::operationAutumn() {
		cout << "Autumn operation on the "<< '"' << name_Child_Composite << '"' << " .\n";
}

Composite_Tree::Composite_Tree(string treeNameArg) : Component(treeNameArg) {};

Composite_Tree::~Composite_Tree() {
	for (auto& child : childrenCopmponents) {
			delete &child;
	}
} 

const int Composite_Tree::getAmountOfLeafs() {
	return this->childrenCopmponents.size();
}


void Composite_Tree::addChildComp(unique_ptr<Component> childCompArg) {
	this->childrenCopmponents.push_back(move(childCompArg));
}

void Composite_Tree::operationAutumn() {
		cout << "\n--- begin autumn operation on the tree.\n";
		for (const auto& child : childrenCopmponents) {
			child->operationAutumn();
		}
}

void Composite_Tree::removeChild(string leafName) {
	auto it = childrenCopmponents.begin();
	while (it != childrenCopmponents.end()) {
		string currLeaf = (*it)->name_Child_Composite;
		if (currLeaf == leafName) {
			childrenCopmponents.erase(it);
			break;
		}
		it++;
	}
}

void Composite_Tree::printLeafs() {
	cout << endl << " The tree has leafs:     ";
	for (const auto& child : childrenCopmponents) {
		cout << child->name_Child_Composite << "    ";
	}
	cout << endl;
}
