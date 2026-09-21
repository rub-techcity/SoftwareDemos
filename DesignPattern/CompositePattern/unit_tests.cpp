#define CATCH_CONFIG_MAIN
#include "catch.hpp"
#include "CompositePattern.h"

using namespace std;

TEST_CASE("main - create two components and composite.")
{
	unique_ptr<Leaf> leafSmall(new Leaf("leaf_small"));
	unique_ptr<Leaf> leafBig(new Leaf("leaf_big"));

	// create a tree, that should have leafs
	Composite_Tree * compositeTree = new Composite_Tree("tree_with_leafs");

	REQUIRE(leafSmall->name_Child_Composite == "leaf_small");
	REQUIRE(leafBig->name_Child_Composite == "leaf_big");

	// grow two leafs on the tree
	compositeTree->addChildComp(move(leafSmall));
	compositeTree->addChildComp(move(leafBig));

	compositeTree->printLeafs();

	REQUIRE(compositeTree->getAmountOfLeafs() == 2);

	// operation on the entire tree
	compositeTree->operationAutumn();

	// now remove a leaf
	cout << endl;
	compositeTree->removeChild("leaf_big");

	REQUIRE(compositeTree->getAmountOfLeafs() == 1);

	cout << " ----- after removing a leaf --------" << endl;
	compositeTree->printLeafs();
}


